#!/usr/bin/env python3
"""Optional real-Chromium smoke checks for the local-first Atlas explorer.

Install with: python -m pip install playwright==1.57.0
              python -m playwright install chromium
Run from any directory: python scripts/browser_smoke.py

This is automated Chromium coverage, not a screen-reader or Firefox audit.
"""

from __future__ import annotations

from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import platform
import threading
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    """Serve only the checked-out repository over loopback."""

    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def local_server():
    handler = partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def run_checks() -> None:
    total = len(json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8")))
    assert total > 0, "expected a non-empty catalog"
    passed: list[str] = []

    with local_server() as base, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        print(f"Platform: {platform.platform()}")
        print(f"Chromium: {browser.version}")
        print("Automated tests: Chromium only; no manual or screen-reader certification.")
        try:
            desktop = browser.new_context(viewport={"width": 1440, "height": 900})
            page = desktop.new_page()
            requests: list[str] = []
            page.on("request", lambda request: requests.append(request.url))
            response = page.goto(base + "/site/", wait_until="load")
            assert response is not None and response.status == 200
            expect(page.locator("#cards article")).to_have_count(total)
            expect(page.locator("#results-status")).to_have_text(
                f"Showing {total} of {total} curated resources."
            )
            assert all(urlsplit(url).hostname == "127.0.0.1" for url in requests), requests
            passed.append("desktop catalog load and local-only requests")

            page.locator("#query").fill("rust")
            assert page.locator("#cards article").count() > 0
            expect(page.locator("#clear-filters")).to_be_enabled()
            page.locator("#category").select_option("programming-languages")
            page.locator("#kind").select_option("official-guide")
            assert page.locator("#cards article").count() > 0
            page.locator("#clear-filters").click()
            expect(page.locator("#query")).to_have_value("")
            expect(page.locator("#cards article")).to_have_count(total)
            passed.append("search, category/kind filters, clear and result counts")

            page.goto(base + "/site/?q=rust&category=programming-languages")
            expect(page.locator("#query")).to_have_value("rust")
            expect(page.locator("#category")).to_have_value("programming-languages")
            assert page.locator("#cards article").count() > 0
            passed.append("shareable URL filter restoration")

            page.goto(base + "/site/")
            expect(page.locator("#cards article")).to_have_count(total)
            page.keyboard.press("Tab")
            assert page.evaluate(
                "document.activeElement?.classList.contains('skip-link')"
            ), "first Tab should reach the skip link"
            assert page.locator(".skip-link").evaluate(
                "el => getComputedStyle(el).outlineStyle !== 'none'"
            ), "skip link should have visible focus"
            page.keyboard.press("/")
            assert page.evaluate("document.activeElement?.id") == "query"
            page.keyboard.type("rust")
            expect(page.locator("#query")).to_have_value("rust")
            page.keyboard.press("Escape")
            expect(page.locator("#query")).to_have_value("")
            passed.append("keyboard skip link, focus indicator, / and Escape")

            desktop.set_offline(True)
            page.locator("#query").fill("python")
            assert page.locator("#cards article").count() > 0
            desktop.set_offline(False)
            passed.append("loaded catalog continues filtering while network is offline")
            desktop.close()

            for width, height in ((360, 780), (390, 844), (768, 1024)):
                context = browser.new_context(viewport={"width": width, "height": height})
                mobile = context.new_page()
                mobile.goto(base + "/site/")
                expect(mobile.locator("#cards article")).to_have_count(total)
                measures = mobile.evaluate("""() => ({
                    viewport: document.documentElement.clientWidth,
                    scrollWidth: document.documentElement.scrollWidth,
                })""")
                assert measures["scrollWidth"] <= measures["viewport"] + 1, (
                    f"horizontal overflow at {width}x{height}: {measures}"
                )
                assert mobile.locator("#query").is_visible()
                assert mobile.locator("#clear-filters").is_visible()
                context.close()
            passed.append("360px, 390px and 768px layouts without horizontal overflow")

            no_js = browser.new_context(java_script_enabled=False)
            fallback = no_js.new_page()
            fallback.goto(base + "/site/")
            link = fallback.locator("noscript a[href='../resources/README.md']")
            expect(link).to_be_visible()
            response = fallback.goto(base + "/resources/README.md")
            assert response is not None and response.status == 200
            no_js.close()
            passed.append("JavaScript-disabled fallback points to local Markdown")

            file_context = browser.new_context()
            file_page = file_context.new_page()
            file_page.goto((ROOT / "site/index.html").as_uri())
            expect(file_page.locator("#results-status")).to_be_visible()
            expect(file_page.locator("#results-status")).to_contain_text(
                "Run a local HTTP server"
            )
            file_context.close()
            passed.append("raw file:// access shows a local-server explanation")
        finally:
            browser.close()

    for name in passed:
        print(f"PASS: {name}")
    print(f"PASS: {len(passed)} automated Chromium smoke checks")


if __name__ == "__main__":
    run_checks()
