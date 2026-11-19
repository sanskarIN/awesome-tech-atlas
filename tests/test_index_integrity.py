"""Bidirectional Atlas catalog/index membership regression tests (stdlib only)."""

import tempfile
import unittest
from pathlib import Path

from scripts import validate


class IndexMembershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "resources").mkdir()
        (self.root / "categories").mkdir()
        for category in validate.CATEGORIES:
            (self.root / "categories" / f"{category}.md").write_text(
                "# Category\n", encoding="utf-8"
            )
        self.records = [
            {
                "id": "python", "name": "Python documentation",
                "category": "programming-languages",
                "subcategory": "Python language",
            },
            {
                "id": "gdb", "name": "GNU GDB documentation",
                "category": "developer-tools",
                "subcategory": "Source-level debugging",
            },
        ]
        self.index_rows = {
            "python": "| [Python documentation](python.md) | Python language | "
                      "[Programming languages](../categories/programming-languages.md) |",
            "gdb": "| [GNU GDB documentation](gdb.md) | Source-level debugging | "
                   "[Developer tools](../categories/developer-tools.md) |",
        }
        self.category_rows = {
            "python": "- **[Python documentation](../resources/python.md):** Short editorial description.",
            "gdb": "- **[GNU GDB documentation](../resources/gdb.md):** Another description.",
        }
        self._write_index()
        self._write_category("programming-languages", "python")
        self._write_category("developer-tools", "gdb")
        for record in self.records:
            (self.root / "resources" / f"{record['id']}.md").write_text(
                "# " + record["name"] + "\n", encoding="utf-8"
            )

    def _write_index(self, *ids):
        ids = ids or ("python", "gdb")
        (self.root / "resources/README.md").write_text(
            "| Resource | Subject | Category |\n| --- | --- | --- |\n"
            + "\n".join(self.index_rows[ident] for ident in ids) + "\n",
            encoding="utf-8",
        )

    def _write_category(self, category, *ids):
        (self.root / "categories" / f"{category}.md").write_text(
            "# Category\n" + "\n".join(self.category_rows[ident] for ident in ids) + "\n",
            encoding="utf-8",
        )

    def _problems(self):
        return validate.validate_index_membership(self.root, self.records)

    def test_matching_catalog_indexes_and_profiles_pass(self):
        self.assertEqual(self._problems(), [])

    def test_missing_and_duplicate_resource_index_rows_are_detected(self):
        self._write_index("python", "python")
        problems = self._problems()
        self.assertTrue(any("duplicates resource: python" in p for p in problems), problems)
        self.assertTrue(any("missing catalog entry: gdb" in p for p in problems), problems)

    def test_index_name_category_and_subcategory_mismatches_are_detected(self):
        bad = self.index_rows["python"].replace(
            "Python documentation", "Python guide"
        ).replace("Python language", "Python syntax").replace(
            "programming-languages.md", "developer-tools.md"
        )
        self.index_rows["python"] = bad
        self._write_index()
        problems = self._problems()
        for field in ("name", "subcategory", "category"):
            self.assertTrue(any(f"python: {field} mismatch" in p for p in problems), problems)

    def test_wrong_category_and_repeated_category_entries_are_detected(self):
        self._write_category("developer-tools", "gdb", "python", "gdb")
        self._write_category("programming-languages")
        problems = self._problems()
        self.assertTrue(any("misplaced resource python" in p for p in problems), problems)
        self.assertTrue(any("duplicate resource gdb" in p for p in problems), problems)
        self.assertTrue(any("missing catalog resource python" in p for p in problems), problems)

    def test_category_display_name_mismatch_is_detected(self):
        self.category_rows["python"] = self.category_rows["python"].replace(
            "Python documentation", "Other Python docs"
        )
        self._write_category("programming-languages", "python")
        self.assertTrue(any("name mismatch for python" in p for p in self._problems()))

    def test_unknown_and_malformed_index_references_are_detected(self):
        self.index_rows["python"] = "| [Unfinished](unfinished.md) | Syntax | "
        self._write_index()
        self._write_category("developer-tools", "gdb", "python")
        problems = self._problems()
        self.assertTrue(any("malformed entry row" in p for p in problems), problems)
        self.assertTrue(any("misplaced resource python" in p for p in problems), problems)

    def test_unknown_catalog_entries_and_untracked_files_are_detected(self):
        self.index_rows["unknown"] = "| [Unknown](unknown.md) | Unknown | "
        self.index_rows["unknown"] += "[Tools](../categories/developer-tools.md) |"
        self._write_index("python", "gdb", "unknown")
        (self.root / "resources/forgotten.md").write_text("# Forgotten\n", encoding="utf-8")
        (self.root / "categories/forgotten.md").write_text("# Forgotten\n", encoding="utf-8")
        problems = self._problems()
        self.assertTrue(any("unknown resource: unknown" in p for p in problems), problems)
        self.assertTrue(any("Uncataloged resource profile: resources/forgotten.md" in p for p in problems), problems)
        self.assertTrue(any("Unrecognized category page: categories/forgotten.md" in p for p in problems), problems)

    def test_category_editorial_summaries_can_differ(self):
        self.category_rows["python"] = (
            "- **[Python documentation](../resources/python.md):** "
            "A deliberately different but valid editorial summary."
        )
        self._write_category("programming-languages", "python")
        self.assertEqual(self._problems(), [])

    def test_fenced_links_do_not_count_as_category_membership(self):
        self._write_category("developer-tools", "gdb")
        path = self.root / "categories/developer-tools.md"
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\n~~~md\n" + self.category_rows["gdb"] + "\n~~~\n",
            encoding="utf-8",
        )
        self.assertEqual(self._problems(), [])


if __name__ == "__main__":
    unittest.main()
