"""Regression tests for explicit curated profile cross-references."""

from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts import atlas
from scripts.navigation_audit import NavigationAuditError, profile_references


class ProfileReferencesTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.directory = self.root / "resources"
        self.directory.mkdir()
        self.records = [
            {
                "id": ident, "name": name, "category": "programming-languages",
                "subcategory": "Example", "kind": "official-docs",
                "summary": "Original description.", "url": "https://example.org/" + ident,
                "verified_on": "2026-11-26",
            }
            for ident, name in (("alpha", "Alpha"), ("beta", "Beta"), ("gamma", "Gamma"),
                                ("delta", "Delta"))
        ]
        self.catalog = self.root / "catalog.json"
        self.catalog.write_text(json.dumps(self.records), encoding="utf-8")
        self.write("alpha", """
[Beta](beta.md)
[Beta again](./beta.md#example)
[Gamma][g]
[Self](alpha.md)
[Unknown](missing.md)
[External](https://example.org/delta.md)
[Outside](../delta.md)

[g]: gamma.md

`[Inline code](delta.md)`
<!-- [Comment](delta.md) -->
~~~text
[Fenced code](delta.md)
~~~
""")
        self.write("beta", "[Alpha](alpha.md?example=1#section)")
        self.write("gamma", "[Alpha][a]\n\n[a]: ./alpha.md")
        self.write("delta", "# No links")

    def write(self, ident, markdown):
        (self.directory / f"{ident}.md").write_text(markdown, encoding="utf-8")

    def report(self, ident):
        return profile_references(self.records, ident, self.root)

    def invoke(self, *args):
        output, error = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            status = atlas.main(["--catalog", str(self.catalog), "related", *args,
                                 "--root", str(self.root)])
        return status, output.getvalue(), error.getvalue()

    def test_bidirectional_links_are_explicit_unique_and_sorted(self):
        report = self.report("alpha")
        self.assertEqual(report["resource"]["id"], "alpha")
        self.assertEqual(report["scanned_profiles"], 4)
        self.assertEqual([item["id"] for item in report["outgoing"]], ["beta", "gamma"])
        self.assertEqual([item["id"] for item in report["incoming"]], ["beta", "gamma"])
        self.assertEqual(report["untracked_outgoing"], ["missing"])
        self.assertEqual(report["outgoing"][0]["profile"], "resources/beta.md")

    def test_graph_is_directional_and_empty_nodes_are_valid(self):
        beta = self.report("beta")
        self.assertEqual([item["id"] for item in beta["outgoing"]], ["alpha"])
        self.assertEqual([item["id"] for item in beta["incoming"]], ["alpha"])
        delta = self.report("delta")
        self.assertEqual(delta["outgoing"], [])
        self.assertEqual(delta["incoming"], [])
        self.assertEqual(delta["untracked_outgoing"], [])

    def test_catalog_order_does_not_change_report(self):
        expected = self.report("alpha")
        self.records.reverse()
        self.assertEqual(self.report("alpha"), expected)

    def test_unknown_id_fails_without_output(self):
        for ident in ("unknown", "Alpha", "../alpha"):
            with self.subTest(ident=ident):
                status, output, error = self.invoke(ident, "--json")
                self.assertEqual(status, 1)
                self.assertEqual(output, "")
                self.assertIn("Unknown resource ID", error)

    def test_missing_unrelated_profile_fails_instead_of_incomplete_incoming_links(self):
        (self.directory / "delta.md").unlink()
        status, output, error = self.invoke("alpha", "--json")
        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("Cannot resolve profile", error)

    def test_invalid_utf8_fails_without_partial_output(self):
        (self.directory / "delta.md").write_bytes(b"\xff")
        status, output, error = self.invoke("alpha", "--json")
        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn("Cannot read", error)

    def test_symlinked_profile_is_rejected(self):
        path = self.directory / "delta.md"
        path.unlink()
        try:
            path.symlink_to(self.directory / "beta.md")
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlink creation unavailable: {exc}")
        with self.assertRaisesRegex(NavigationAuditError, "Not a regular profile"):
            self.report("alpha")

    def test_json_and_text_cli(self):
        status, output, error = self.invoke("alpha", "--json")
        self.assertEqual((status, error), (0, ""))
        self.assertEqual(json.loads(output), self.report("alpha"))
        status, output, error = self.invoke("alpha")
        self.assertEqual((status, error), (0, ""))
        self.assertIn("Links to (2):", output)
        self.assertIn("Linked from (2):", output)
        self.assertIn("Untracked outgoing IDs: missing", output)

    def test_real_catalog_has_python_to_rust_reference(self):
        records = atlas.load_catalog()
        python = profile_references(records, "python", atlas.ROOT)
        rust = profile_references(records, "rust", atlas.ROOT)
        self.assertEqual(python["scanned_profiles"], len(records))
        self.assertIn("rust", [item["id"] for item in python["outgoing"]])
        self.assertIn("python", [item["id"] for item in rust["incoming"]])


if __name__ == "__main__":
    unittest.main()
