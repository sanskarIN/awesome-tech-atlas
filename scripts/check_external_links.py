#!/usr/bin/env python3
"""Network-dependent official URL audit. Distinguish bad links from HTTP blocks."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "AwesomeTechAtlas-LinkCheck/1.0 (+https://github.com/sanskarIN/awesome-tech-atlas)"
TIMEOUT = 12


def probe(item: dict[str, str]) -> tuple[str, str, str]:
    url = item["url"]
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*"}
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                return item["id"], "ok", f"HTTP {response.status}; {response.url}"
        except urllib.error.HTTPError as exc:
            # A blocked or unimplemented HEAD request does not prove GET is broken.
            if method == "HEAD" and exc.code in {400, 403, 404, 405, 410, 501}:
                continue
            if exc.code in {401, 403, 429, 500, 502, 503, 504}:
                return item["id"], "review", f"HTTP {exc.code}: possible network block or temporary server error"
            return item["id"], "broken", f"HTTP {exc.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            # Retry with GET when the server or proxy refuses HEAD.
            if method == "HEAD":
                continue
            return item["id"], "review", f"Network error: {exc}"
    return item["id"], "review", "Unsupported HEAD/GET response"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Fail when a URL is positively broken.")
    args = parser.parse_args()
    records = json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(probe, records))
    counts = {"ok": 0, "review": 0, "broken": 0}
    for resource_id, status, detail in results:
        counts[status] += 1
        print(f"{status.upper():6} {resource_id}: {detail}")
    print(f"Link audit: {counts['ok']} OK, {counts['review']} manual review, {counts['broken']} broken")
    # HTTP 403/429/timeouts cannot prove a link is invalid and need human assessment.
    return 1 if args.strict and counts["broken"] else 0


if __name__ == "__main__":
    sys.exit(main())
