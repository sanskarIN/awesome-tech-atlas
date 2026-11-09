#!/usr/bin/env python3
"""Build a self-contained, deterministic offline Atlas HTML snapshot (stdlib only).

This is a local opt-in export. It never publishes, uploads, or enables Pages.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "awesome-tech-atlas-offline.html"
HTML_SCRIPT = '<script type="module" src="./app.mjs"></script>'
HTML_STYLES = '<link rel="stylesheet" href="./styles.css">'
HTML_DOWNLOAD = '<a href="../data/resources.json" class="data-link" download>Get catalog JSON</a>'
APP_IMPORT = '''import {
  countBy, filtersToQuery, parseFilters, searchResources,
} from "./search.mjs";
'''
REQUIRED = ("id", "name", "category", "kind", "subcategory", "summary", "url", "verified_on")
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

DOWNLOAD_SCRIPT = r"""
document.getElementById("download-catalog").addEventListener("click", () => {
  const content = JSON.stringify(globalThis.__ATLAS_EMBEDDED_CATALOG__, null, 2) + "\n";
  const blob = new Blob([content], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "resources.json";
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
});
"""


def replace_exactly_once(source: str, old: str, new: str) -> str:
    """Fail closed when the source page's expected structure has changed."""
    if source.count(old) != 1:
        raise ValueError(f"Expected exactly one occurrence of {old[:72]!r}")
    return source.replace(old, new, 1)


def verify_records(records: object) -> list[dict[str, str]]:
    if not isinstance(records, list) or not records:
        raise ValueError("Catalog must be a non-empty list of resource records.")
    seen: set[str] = set()
    for index, entry in enumerate(records, 1):
        if not isinstance(entry, dict) or any(
            not isinstance(entry.get(field), str) for field in REQUIRED
        ):
            raise ValueError(f"Resource #{index}: missing or invalid required fields.")
        identifier = entry["id"]
        if not SLUG.fullmatch(identifier) or identifier in seen:
            raise ValueError(f"Resource #{index}: duplicate or invalid id.")
        seen.add(identifier)
        parsed = urlsplit(entry["url"])
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError(f"Resource #{index}: upstream URL must be HTTPS without credentials.")
    return records


def script_safe_json(records: object) -> str:
    """Prevent a catalog value from terminating the embedding <script> element."""
    encoded = json.dumps(records, ensure_ascii=True, separators=(",", ":"))
    return (
        encoded.replace("&", r"\u0026")
        .replace("<", r"\u003c")
        .replace(">", r"\u003e")
        .replace("\u2028", r"\u2028")
        .replace("\u2029", r"\u2029")
    )


def load_profiles(root: Path, records: list[dict[str, str]]) -> dict[str, str]:
    """Read every original profile verbatim. Missing or mismatched files fail the build."""
    profiles: dict[str, str] = {}
    for entry in records:
        path = root / "resources" / (entry["id"] + ".md")
        body = path.read_text(encoding="utf-8")
        if not body.strip() or entry["url"] not in body:
            raise ValueError(f"Profile is empty or missing the official URL: {entry['id']}")
        profiles[entry["id"]] = body
    return profiles


def noscript_index(records: list[dict[str, str]], profiles: dict[str, str]) -> str:
    items = []
    for entry in records:
        name = html.escape(entry["name"])
        summary = html.escape(entry["summary"])
        url = html.escape(entry["url"], quote=True)
        body = html.escape(profiles[entry["id"]])
        items.append(
            f'            <li><details><summary><strong>{name}</strong> — {summary}</summary>'
            f'<pre>{body}</pre>'
            f'<p><a href="{url}" rel="noreferrer">Official documentation (online)</a></p>'
            f'</details></li>'
        )
    return (
        '        <noscript>\n'
        '          <section class="fallback" aria-labelledby="offline-fallback">\n'
        '            <h3 id="offline-fallback">Resources without JavaScript</h3>\n'
        '            <p>Local catalog snapshot. The following upstream links need internet access.</p>\n'
        '            <ul>\n' + "\n".join(items) + '\n            </ul>\n'
        '          </section>\n'
        '        </noscript>'
    )


def build_offline_html(root: Path = ROOT, records: object | None = None) -> str:
    root = Path(root)
    if records is None:
        records = json.loads((root / "data/resources.json").read_text(encoding="utf-8"))
    catalog = verify_records(records)
    profiles = load_profiles(root, catalog)

    page = (root / "site/index.html").read_text(encoding="utf-8")
    styles = (root / "site/styles.css").read_text(encoding="utf-8")
    search = (root / "site/search.mjs").read_text(encoding="utf-8")
    app = (root / "site/app.mjs").read_text(encoding="utf-8")

    if not app.startswith(APP_IMPORT):
        raise ValueError("Unexpected browser imports; inspect app.mjs before rebuilding.")
    app = app[len(APP_IMPORT):]
    # Transform only the explicitly supported pure-function ES module exports.
    search = re.sub(r"(?m)^export (?=function )", "", search)
    combined = search + "\n" + app
    if re.search(r"(?m)^\s*(?:import|export)\b", combined) or "import.meta" in combined:
        raise ValueError("Unsupported ES module syntax in offline snapshot.")
    if re.search(r"</script", combined, flags=re.IGNORECASE):
        raise ValueError("Unescaped script terminator in trusted JS sources.")
    if re.search(r"</style", styles, flags=re.IGNORECASE):
        raise ValueError("Unescaped style terminator in trusted CSS source.")

    code = (
        '"use strict";\n'
        f'globalThis.__ATLAS_EMBEDDED_CATALOG__ = {script_safe_json(catalog)};\n'
        f'globalThis.__ATLAS_EMBEDDED_PROFILES__ = {script_safe_json(profiles)};\n'
        + combined + "\n" + DOWNLOAD_SCRIPT
    )
    page = replace_exactly_once(page, HTML_STYLES, "<style>\n" + styles + "\n</style>")
    page = replace_exactly_once(page, HTML_SCRIPT, "")
    page = replace_exactly_once(
        page, HTML_DOWNLOAD,
        '<button type="button" class="data-link" id="download-catalog">'
        'Download snapshot JSON</button>',
    )
    page = replace_exactly_once(
        page, "<title>Explore resources | Awesome Tech Atlas</title>",
        "<title>Offline explorer | Awesome Tech Atlas</title>",
    )
    page, count = re.subn(r"<noscript>[\s\S]*?</noscript>", lambda match: noscript_index(catalog, profiles), page)
    if count != 1:
        raise ValueError("Expected exactly one noscript fallback.")
    page = replace_exactly_once(
        page, "</body>",
        '<script>\n' + code + '\n</script>\n</body>',
    )
    return page


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="Destination HTML file (default: dist/awesome-tech-atlas-offline.html)",
    )
    args = parser.parse_args(argv)
    result = build_offline_html()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"Built offline catalog: {args.output} ({len(result.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
