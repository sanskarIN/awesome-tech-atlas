"""Tests for the atlas command-line interface and search semantics."""

import contextlib
import csv
from datetime import date
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
        self.assertEqual(stats["resources"], 42)
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

    def test_csv_serialization_guards_formulas_quotes_and_unicode(self):
        risky = record("one", "  =HYPERLINK(\"https://example.org\")")
        risky["summary"] = "\t+SUM(1,2)"
        risky["subcategory"] = 'A "quoted", field'
        plain = record("two", "Café")
        output = atlas.resources_to_csv([risky, plain])
        self.assertTrue(output.endswith("\r\n"))
        self.assertNotIn("\r\r\n", output)
        self.assertEqual(output.count("\r\n"), 3)
        rows = list(csv.reader(StringIO(output, newline="")))
        self.assertEqual(rows[0], list(atlas.CSV_COLUMNS))
        self.assertEqual(rows[1][1], "'  =HYPERLINK(\"https://example.org\")")
        self.assertEqual(rows[1][3], 'A "quoted", field')
        self.assertEqual(rows[1][5], "'\t+SUM(1,2)")
        self.assertEqual(rows[2][1], "Café")
        self.assertEqual(atlas.resources_to_csv([]), atlas.resources_to_csv([risky]).split("\r\n")[0] + "\r\n")

    def test_cli_csv_respects_search_and_outputs_header_for_no_results(self):
        buffer = StringIO()
        with contextlib.redirect_stdout(buffer):
            status = atlas.main(["search", "rust", "--category", "programming-languages", "--limit", "1", "--csv"])
        self.assertEqual(status, 0)
        rows = list(csv.DictReader(StringIO(buffer.getvalue())))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "rust")
        self.assertIn("\r\n", buffer.getvalue())

        buffer = StringIO()
        with contextlib.redirect_stdout(buffer):
            status = atlas.main(["search", "nonexistent-atlas-query-xyz", "--csv"])
        self.assertEqual(status, 0)
        self.assertEqual(list(csv.DictReader(StringIO(buffer.getvalue()))), [])

    def test_cli_csv_and_json_cannot_be_combined(self):
        with contextlib.redirect_stderr(StringIO()), self.assertRaises(SystemExit) as raised:
            atlas.make_parser().parse_args(["search", "rust", "--csv", "--json"])
        self.assertEqual(raised.exception.code, 2)

    def test_review_queue_is_inclusive_sorted_and_filterable(self):
        entries = [
            record("b", "Bravo"), record("a", "Alpha"),
            record("c", "Current"), record("d", "Oldest"),
        ]
        entries[0]["verified_on"] = "2026-08-18"  # exactly 90 days
        entries[1]["verified_on"] = "2026-08-18"
        entries[2]["verified_on"] = "2026-08-19"  # only 89 days
        entries[3]["verified_on"] = "2026-07-01"
        entries[3]["category"] = "web-development"

        original = json.dumps(entries)
        all_due = atlas.inspection_queue(entries, date(2026, 11, 16), 90)
        self.assertEqual([item["id"] for item in all_due], ["d", "a", "b"])
        self.assertEqual(all_due[0]["profile"], "resources/d.md")
        self.assertEqual(all_due[1]["age_days"], 90)
        self.assertEqual(
            [item["id"] for item in atlas.inspection_queue(
                entries, date(2026, 11, 16), 90, category="programming-languages"
            )], ["a", "b"],
        )
        self.assertEqual(
            atlas.inspection_queue(entries, date(2026, 11, 16), 90, kind="reference"),
            [],
        )
        self.assertEqual(json.dumps(entries), original)

    def test_review_queue_dates_reject_invalid_input(self):
        for invalid in ("2026-02-30", "2026-2-03", "yesterday"):
            with self.subTest(date=invalid):
                with self.assertRaises(Exception):
                    atlas.iso_date(invalid)
        for invalid in ("-1", "no"):
            with self.subTest(days=invalid):
                with self.assertRaises(Exception):
                    atlas.nonnegative_integer(invalid)
        self.assertEqual(atlas.nonnegative_integer("0"), 0)

        item = record("invalid", "Invalid")
        item["verified_on"] = "2026-02-30"
        with self.assertRaises(atlas.CatalogError):
            atlas.inspection_queue([item], date(2026, 11, 16))

    def test_review_queue_cli_json_reports_total_before_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resources.json"
            entries = [record("a", "Alpha"), record("b", "Beta")]
            for entry in entries:
                entry["verified_on"] = "2026-08-01"
            path.write_text(json.dumps(entries), encoding="utf-8")
            output = StringIO()
            with contextlib.redirect_stdout(output):
                result = atlas.main([
                    "--catalog", str(path), "review-queue",
                    "--as-of", "2026-11-16", "--days", "90",
                    "--limit", "1", "--json",
                ])
            self.assertEqual(result, 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report["as_of"], "2026-11-16")
            self.assertEqual(report["matching_resources"], 2)
            self.assertEqual(report["shown_resources"], 1)
            self.assertEqual(report["resources"][0]["id"], "a")

            output = StringIO()
            with contextlib.redirect_stdout(output):
                result = atlas.main([
                    "--catalog", str(path), "review-queue",
                    "--as-of", "2026-11-16", "--days", "200",
                ])
            self.assertEqual(result, 0)
            self.assertIn("0 resource(s)", output.getvalue())
            self.assertIn("not proof of a broken link", output.getvalue())

    def test_positive_integer(self):
        for invalid in ("0", "-1", "hello"):
            with self.subTest(value=invalid):
                with self.assertRaises(Exception):
                    atlas.positive_integer(invalid)
        self.assertEqual(atlas.positive_integer("12"), 12)


if __name__ == "__main__":
    unittest.main()
