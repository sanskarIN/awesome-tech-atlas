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
        self.assertIn("offline-profile-dialog", parser.ids)
        self.assertIn("offline-profile-title", parser.ids)
        self.assertIn("offline-profile-markdown", parser.ids)
        self.assertIn("offline-profile-close", parser.ids)
        self.assertEqual(parser.scripts, ["./app.mjs"])
        self.assertEqual(parser.styles, ["./styles.css"])
        for asset in ("site/app.mjs", "site/search.mjs", "site/styles.css"):
            self.assertTrue((ROOT / asset).is_file(), asset)

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

    def test_no_automatic_pages_workflow(self):
        workflows = ROOT / ".github/workflows"
        text = "\n".join(path.read_text(encoding="utf-8") for path in workflows.glob("*.yml"))
        self.assertNotIn("actions/deploy-pages", text)
        self.assertNotIn("pages: write", text)


if __name__ == "__main__":
    unittest.main()
