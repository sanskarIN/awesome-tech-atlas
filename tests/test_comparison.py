"""Regression tests for explicit, read-only terminal resource comparisons."""

import contextlib
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts import atlas


def record(ident, name):
    return {
        "id": ident,
        "name": name,
        "category": "programming-languages",
        "subcategory": "Language reference",
        "kind": "official-docs",
        "summary": "A curated description.",
        "url": "https://example.org/" + ident,
        "verified_on": "2026-11-08",
    }


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            record("alpha", "Alpha"),
            record("beta", "Béta"),
            record("gamma", "Gamma"),
        ]
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.catalog = Path(self.directory.name) / "resources.json"
        self.catalog.write_text(json.dumps(self.records), encoding="utf-8")

    def invoke(self, *args):
        output, error = StringIO(), StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = atlas.main(["--catalog", str(self.catalog), "compare", *args])
        return status, output.getvalue(), error.getvalue()

    def test_resolves_exact_ids_in_selection_order_without_mutation(self):
        original = deepcopy(self.records)
        selected = atlas.compare_records(self.records, ["gamma", "alpha"])
        self.assertEqual(selected, [original[2], original[0]])
        self.assertEqual(self.records, original)

    def test_json_returns_full_original_records_in_selection_order(self):
        before = self.catalog.read_bytes()
        status, output, error = self.invoke("beta", "gamma", "alpha", "--json")
        self.assertEqual(status, 0)
        self.assertEqual(error, "")
        self.assertEqual(json.loads(output), [self.records[1], self.records[2], self.records[0]])
        self.assertIn("Béta", output)
        self.assertEqual(self.catalog.read_bytes(), before)

    def test_human_output_includes_context_and_no_ranking_claim(self):
        status, output, error = self.invoke("beta", "alpha")
        self.assertEqual((status, error), (0, ""))
        self.assertLess(output.index("Béta [beta]"), output.index("Alpha [alpha]"))
        for part in ("Topic:", "Subcategory:", "Resource type:", "Summary:",
                     "Official source:", "Last source inspection:",
                     "resources/beta.md", "not a ranking"):
            self.assertIn(part, output)

    def test_invalid_selections_fail_without_partial_output(self):
        for ids, reason in (
            (["alpha"], "two or three"),
            (["alpha", "beta", "gamma", "delta"], "two or three"),
            (["alpha", "alpha"], "distinct"),
            (["alpha", "missing"], "Unknown resource ID"),
            (["ALPHA", "beta"], "Unknown resource ID"),
            (["alph", "beta"], "Unknown resource ID"),
        ):
            for options in ([], ["--json"]):
                with self.subTest(ids=ids, options=options):
                    status, output, error = self.invoke(*ids, *options)
                    self.assertNotEqual(status, 0)
                    self.assertEqual(output, "")
                    self.assertIn(reason, error)

    def test_missing_arguments_are_parser_error(self):
        with contextlib.redirect_stderr(StringIO()), self.assertRaises(SystemExit) as exc:
            atlas.main(["--catalog", str(self.catalog), "compare"])
        self.assertEqual(exc.exception.code, 2)

    def test_real_catalog_selection(self):
        records = atlas.load_catalog()
        selected = atlas.compare_records(records, ["sqlite", "postgresql"])
        self.assertEqual([entry["id"] for entry in selected], ["sqlite", "postgresql"])
        for entry in selected:
            self.assertTrue((atlas.ROOT / "resources" / (entry["id"] + ".md")).is_file())


if __name__ == "__main__":
    unittest.main()
