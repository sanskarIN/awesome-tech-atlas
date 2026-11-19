"""Navigation coverage tests: direct, reference and editorial reporting."""

import contextlib
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts import atlas
from scripts.navigation_audit import (
    NavigationAuditError, navigation_report,
)


def sample(ident: str, name: str, category: str = "programming-languages") -> dict[str, str]:
    return {
        "id": ident, "name": name, "category": category,
        "subcategory": "Learning", "kind": "official-guide",
        "summary": "Useful official learning documentation.",
        "url": "https://example.invalid/" + ident,
        "verified_on": "2026-11-08",
    }


class NavigationCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "guides").mkdir()
        (self.root / "comparisons").mkdir()
        (self.root / "resources").mkdir()
        (self.root / "data").mkdir()
        self.records = [
            sample("alpha", "Alpha"), sample("beta", "Beta"),
            sample("gamma", "Gamma", "compiler-development"),
            sample("delta", "Delta", "compiler-development"),
        ]
        self.catalog = self.root / "data/resources.json"
        self.catalog.write_text(json.dumps(self.records), encoding="utf-8")
        (self.root / "guides/learn.md").write_text(
            "# Learn\n"
            "[Alpha](../resources/alpha.md) and [Again](../resources/alpha.md#why)\n"
            "[Beta][b] and [Another][b]\n"
            "[b]: ../resources/beta.md \"Resource\"\n"
            "[Unknown](../resources/untracked.md)\n"
            "\x60[Invisible](../resources/delta.md)\x60\n"
            "~~~md\n[Demo](../resources/delta.md)\n~~~\n"
            "<!-- [Commented](../resources/delta.md) -->\n",
            encoding="utf-8",
        )
        (self.root / "comparisons/choose.md").write_text(
            "[Alpha](../resources/alpha.md?view=1#why)\n"
            "[Gamma](../resources/gamma.md)\n"
            "[External](https://example.invalid/resources/delta.md)\n",
            encoding="utf-8",
        )

    def report(self, category=""):
        return navigation_report(self.records, self.root, category)

    def test_counts_distinguish_docs_and_deduplicate_per_file(self):
        report = self.report()
        self.assertEqual(report["source_documents"], {"guides": 1, "comparisons": 1})
        self.assertEqual(report["catalog_resources"], 4)
        self.assertEqual(report["linked_in_guides"], 2)
        self.assertEqual(report["linked_in_comparisons"], 2)
        self.assertEqual(report["linked_in_either"], 3)
        self.assertEqual(report["unlinked_total"], 1)
        self.assertEqual(report["unlinked_resources"][0]["id"], "delta")

    def test_per_resource_document_paths_and_forward_references(self):
        by_id = {item["id"]: item for item in self.report()["resources"]}
        self.assertEqual(by_id["alpha"]["guides"], ["guides/learn.md"])
        self.assertEqual(by_id["alpha"]["comparisons"], ["comparisons/choose.md"])
        self.assertEqual(by_id["beta"]["guides"], ["guides/learn.md"])
        self.assertEqual(by_id["beta"]["comparisons"], [])
        self.assertEqual(by_id["gamma"]["guides"], [])
        self.assertEqual(by_id["gamma"]["comparisons"], ["comparisons/choose.md"])
        self.assertEqual(by_id["delta"]["guides"], [])

    def test_untracked_profile_links_are_reported_without_claiming_quality(self):
        report = self.report()
        self.assertEqual(report["untracked_profile_links"], [
            {"source": "guides/learn.md", "profile": "resources/untracked.md"}
        ])
        self.assertIn("not a resource quality", report["scope"])

    def test_category_filter_narrows_resources_not_scanned_documents(self):
        report = self.report("compiler-development")
        self.assertEqual(report["catalog_resources"], 2)
        self.assertEqual(report["linked_in_either"], 1)
        self.assertEqual(report["unlinked_total"], 1)
        self.assertEqual(
            report["categories"],
            [{"category": "compiler-development", "resources": 2,
              "in_guides": 0, "in_comparisons": 1, "in_either": 1}],
        )
        self.assertEqual(report["source_documents"], {"guides": 1, "comparisons": 1})

    def test_unknown_category_returns_empty_scope_not_fake_coverage(self):
        report = self.report("no-category")
        self.assertEqual(report["catalog_resources"], 0)
        self.assertEqual(report["categories"], [])
        self.assertEqual(report["unlinked_resources"], [])

    def test_no_document_sources_is_an_error(self):
        (self.root / "guides/learn.md").unlink()
        (self.root / "comparisons/choose.md").unlink()
        with self.assertRaisesRegex(NavigationAuditError, "No guides"):
            self.report()

    def test_invalid_reference_definition_is_an_error(self):
        (self.root / "guides/learn.md").write_text(
            "[Guide][bad]\n[bad]:\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(NavigationAuditError, "invalid reference"):
            self.report()

    def test_cli_json_filter_and_unlinked_limit(self):
        output = StringIO()
        with contextlib.redirect_stdout(output):
            status = atlas.main([
                "--catalog", str(self.catalog), "navigation-audit",
                "--root", str(self.root), "--category", "compiler-development",
                "--limit", "1", "--json",
            ])
        self.assertEqual(status, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["catalog_resources"], 2)
        self.assertEqual(payload["unlinked_total"], 1)
        self.assertEqual(payload["shown_unlinked"], 1)
        self.assertEqual([x["id"] for x in payload["unlinked_resources"]], ["delta"])

    def test_cli_text_report_is_actionable(self):
        output = StringIO()
        with contextlib.redirect_stdout(output):
            status = atlas.main([
                "--catalog", str(self.catalog), "navigation-audit",
                "--root", str(self.root), "--limit", "1",
            ])
        self.assertEqual(status, 0)
        self.assertIn("guide", output.getvalue())
        self.assertIn("unlinked", output.getvalue().lower())
        self.assertIn("resources/delta.md", output.getvalue())
        self.assertIn("untracked.md", output.getvalue())

    def test_cli_unreadable_root_returns_error_code(self):
        errors = StringIO()
        with contextlib.redirect_stderr(errors):
            status = atlas.main([
                "--catalog", str(self.catalog), "navigation-audit",
                "--root", str(self.root / "missing"),
            ])
        self.assertEqual(status, 2)
        self.assertIn("No guides", errors.getvalue())

    def test_cli_positive_limit_is_required(self):
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(StringIO()):
            atlas.make_parser().parse_args(["navigation-audit", "--limit", "0"])
        self.assertEqual(raised.exception.code, 2)

    def test_real_catalog_report_is_deterministic_and_read_only(self):
        records = atlas.load_catalog()
        first = navigation_report(records, atlas.ROOT)
        second = navigation_report(records, atlas.ROOT)
        self.assertEqual(first, second)
        self.assertEqual(first["catalog_resources"], len(records))
        self.assertEqual(first["source_documents"]["guides"] >= 1, True)
        self.assertEqual(first["source_documents"]["comparisons"] >= 1, True)
        self.assertTrue(all(item["profile"].endswith(".md") for item in first["resources"]))


if __name__ == "__main__":
    unittest.main()
