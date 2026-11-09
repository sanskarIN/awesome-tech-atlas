"""Regression checks for reproducible, single-file offline HTML exports."""

import contextlib
from html.parser import HTMLParser
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts import build_offline

ROOT = Path(__file__).resolve().parents[1]


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.stylesheets = []
        self.buttons = []
        self.fallbacks = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "script":
            self.scripts.append(attrs)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.stylesheets.append(attrs)
        if tag == "button":
            self.buttons.append(attrs.get("id"))
        if tag == "noscript":
            self.fallbacks += 1


class OfflineBuilderTests(unittest.TestCase):
    def test_single_file_embeds_every_resource_and_has_no_external_assets(self):
        document = build_offline.build_offline_html()
        parser = Assets()
        parser.feed(document)

        self.assertEqual(len(parser.scripts), 1)
        self.assertEqual(parser.scripts[0], {})
        self.assertEqual(parser.stylesheets, [])
        self.assertEqual(parser.fallbacks, 1)
        self.assertIn("download-catalog", parser.buttons)
        self.assertNotIn('src="./app.mjs"', document)
        self.assertNotIn('href="./styles.css"', document)
        self.assertNotIn("import.meta", document)
        self.assertIn("globalThis.__ATLAS_EMBEDDED_CATALOG__", document)
        self.assertIn("Rust language", document)

        records = json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8"))
        self.assertEqual(len(records), 30)
        for record in records:
            self.assertIn(record["id"], document)
            self.assertIn(record["url"], document)

    def test_export_is_deterministic_and_safe_for_catalog_html(self):
        records = json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8"))
        records[0]["name"] = '</script><script>alert("not run")</script>'
        records[0]["summary"] = '<img src=x onerror="alert(1)"> & example'
        document = build_offline.build_offline_html(records=records)

        self.assertNotIn('</script><script>alert', document)
        self.assertNotIn('<img src=x onerror', document)
        self.assertIn(r'\u003c/script\u003e', document)
        self.assertIn("&lt;img src=x onerror=", document)
        self.assertEqual(document, build_offline.build_offline_html(records=records))

    def test_rejects_duplicate_ids_and_unsafe_urls(self):
        records = json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8"))
        dup = [records[0], records[0]]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            build_offline.build_offline_html(records=dup)

        fake = [dict(records[0])]
        fake[0]["url"] = "javascript:alert(1)"
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            build_offline.build_offline_html(records=fake)

    def test_cli_writes_specified_output(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / "nested" / "atlas.html"
            with contextlib.redirect_stdout(StringIO()):
                status = build_offline.main(["--output", str(filename)])
            self.assertEqual(status, 0)
            self.assertTrue(filename.exists())
            self.assertIn("Offline explorer", filename.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
