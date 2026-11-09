"""Tests for the atlas command-line interface and search semantics."""

import contextlib
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts import atlas


def record(ident, name, summary="An official tool reference for testing."):
    return {
        "id": ident,
        "name": name,
        "category": "programming-languages",
        "subcategory": "Language tooling",
        "kind": "official-docs",
        "url": "https://example.org/" + ident,
        "summary": summary,
        "verified_on": "2026-11-08",
    }


class AtlasExplorerTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(atlas.normalize_text("Café / Scikit-Learn!"), "cafe scikit learn")
        self.assertEqual(atlas.normalize_text("RUST  & Python"), "rust python")

    def test_search_and_ranking(self):
        entries = [
            record("a", "Python"),
            record("b", "Rust", "A guide for Python bindings and interfaces."),
            record("c", "Python reference"),
        ]
        output = atlas.search_records(entries, "python")
        self.assertEqual([item["id"] for item in output], ["a", "c", "b"])
        self.assertEqual(atlas.search_records(entries, "python absent"), [])
        self.assertEqual(len(atlas.search_records(entries, "", limit=2)), 2)

    def test_filters_are_exact_and_case_sensitive_slugs(self):
        entries = [record("a", "Python"), record("b", "Rust")]
        entries[1]["category"] = "systems-programming"
        self.assertEqual(
            [e["id"] for e in atlas.search_records(entries, category="systems-programming")],
            ["b"],
        )
        self.assertEqual(atlas.search_records(entries, kind="official-guide"), [])

    def test_catalog_rejects_invalid_shapes_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resources.json"
            for invalid in ({}, [record("x", "Example"), record("x", "Again")], [{"name": "Incomplete"}]):
                path.write_text(json.dumps(invalid), encoding="utf-8")
                with self.subTest(value=invalid):
                    with self.assertRaises(atlas.CatalogError):
                        atlas.load_catalog(path)

    def test_cli_json_output_and_missing_id(self):
        output = StringIO()
        with contextlib.redirect_stdout(output):
            result = atlas.main(["stats", "--json"])
        self.assertEqual(result, 0)
        stats = json.loads(output.getvalue())
        self.assertEqual(stats["resources"], 30)
        self.assertEqual(stats["categories"], 19)

        error = StringIO()
        with contextlib.redirect_stderr(error):
            result = atlas.main(["show", "not-a-listed-resource"])
        self.assertEqual(result, 1)
        self.assertIn("Unknown resource ID", error.getvalue())

    def test_cli_search_has_real_profile_and_official_url(self):
        output = StringIO()
        with contextlib.redirect_stdout(output):
            result = atlas.main(["search", "rust", "--limit", "1", "--json"])
        self.assertEqual(result, 0)
        items = json.loads(output.getvalue())
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]["url"].startswith("https://"))
        self.assertTrue((atlas.ROOT / "resources" / (items[0]["id"] + ".md")).is_file())

    def test_positive_integer(self):
        for invalid in ("0", "-1", "hello"):
            with self.subTest(value=invalid):
                with self.assertRaises(Exception):
                    atlas.positive_integer(invalid)
        self.assertEqual(atlas.positive_integer("12"), 12)


if __name__ == "__main__":
    unittest.main()
