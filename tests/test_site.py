"""Smoke tests for the static explorer's basic file layout and safe DOM conventions."""

from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExplorerParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.labels: set[str] = set()
        self.scripts: list[str] = []
        self.styles: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "label" and "for" in values:
            self.labels.add(values["for"])
        if tag == "script" and "src" in values:
            self.scripts.append(values["src"])
        if tag == "link" and values.get("rel") == "stylesheet":
            self.styles.append(values["href"])


class SiteTests(unittest.TestCase):
    def test_html_is_local_and_has_form_labels(self):
        parser = ExplorerParser()
        parser.feed((ROOT / "site/index.html").read_text(encoding="utf-8"))
        self.assertIn("explore", parser.ids)
        for field in ("query", "category", "kind"):
            self.assertIn(field, parser.ids)
            self.assertIn(field, parser.labels)
        self.assertIn("results-status", parser.ids)
        self.assertIn("load-fallback", parser.ids)
        self.assertIn("export-results", parser.ids)
        for element in ("compare-status", "compare-panel", "comparison-table", "clear-comparison"):
            self.assertIn(element, parser.ids)
        self.assertIn("offline-profile-dialog", parser.ids)
        self.assertIn("offline-profile-title", parser.ids)
        self.assertIn("offline-profile-markdown", parser.ids)
        self.assertIn("offline-profile-close", parser.ids)
        self.assertEqual(parser.scripts, ["./app.mjs"])
        self.assertEqual(parser.styles, ["./styles.css"])
        for asset in ("site/app.mjs", "site/search.mjs", "site/styles.css"):
            self.assertTrue((ROOT / asset).is_file(), asset)

    def test_no_script_fallback_uses_local_markdown(self):
        content = (ROOT / "site/index.html").read_text(encoding="utf-8")
        self.assertEqual(content.count("<noscript>"), 1)
        fallback = content.split("<noscript>", 1)[1].split("</noscript>", 1)[0]
        self.assertIn('href="../resources/README.md"', fallback)
        self.assertNotIn("https://github.com/", fallback)
        self.assertTrue((ROOT / "resources/README.md").is_file())

    def test_initial_page_explains_file_url_loading_failure(self):
        content = (ROOT / "site/index.html").read_text(encoding="utf-8")
        self.assertIn("Run a local HTTP server", content)
        self.assertIn("file://", content)

    def test_client_renders_untrusted_catalog_as_text(self):
        app = (ROOT / "site/app.mjs").read_text(encoding="utf-8")
        self.assertIn("textContent", app)
        self.assertIn('url.protocol === "https:"', app)
        self.assertIn("../data/resources.json", app)
        self.assertIn("__ATLAS_EMBEDDED_PROFILES__", app)
        self.assertIn("markdown.textContent =", app)
        self.assertIn("dialog.showModal()", app)
        self.assertIn("loadFallback.hidden = false", app)
        self.assertNotIn(".innerHTML", app)
        self.assertNotIn("localStorage", app)
        self.assertNotIn("sessionStorage", app)

    def test_pages_deployment_requires_main_and_passing_build(self):
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertIn("actions/upload-pages-artifact@v3", workflow)
        self.assertIn("actions/deploy-pages@v4", workflow)
        self.assertIn("python3 scripts/validate.py", workflow)
        self.assertIn("python3 scripts/build_pages.py", workflow)
        self.assertIn("needs: build", workflow)
        self.assertIn("if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'", workflow)
        self.assertIn("pages: write", workflow)
        self.assertIn("id-token: write", workflow)


if __name__ == "__main__":
    unittest.main()
