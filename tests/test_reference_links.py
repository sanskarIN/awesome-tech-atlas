"""Regression cases for explicit Markdown reference links and navigation."""

from pathlib import Path
import tempfile
import unittest

from scripts import validate
from scripts.reference_links import (
    normalize_label, prose_lines, scan_reference_links,
)


class ReferenceLinkTests(unittest.TestCase):
    def test_label_normalization_and_forward_reference(self):
        doc = (
            "Read [Rust][ RUST   DOCS ] first.\n"
            "\n[rust docs]: resources/rust.md#start \"Rust manual\"\n"
        )
        definitions, usages, errors = scan_reference_links(doc)
        self.assertEqual(errors, [])
        self.assertEqual(usages[0].label, "rust docs")
        self.assertEqual(definitions["rust docs"].destination, "resources/rust.md#start")
        self.assertEqual(normalize_label("  CAFÉ    HOWTO "), "café howto")

    def test_collapsed_reference_and_image(self):
        definitions, usages, errors = scan_reference_links(
            "Read [manual][] and view ![diagram][figure].\n"
            "[manual]: ./guide.md\n[figure]: ./figure.png\n"
        )
        self.assertEqual(errors, [])
        self.assertEqual([usage.label for usage in usages], ["manual", "figure"])
        self.assertEqual(len(definitions), 2)

    def test_duplicate_reference_definitions_are_diagnosed(self):
        definitions, uses, errors = scan_reference_links(
            "[Guide][docs]\n[docs]: a.md\n[DOCS]: b.md\n"
        )
        self.assertEqual(definitions["docs"].destination, "a.md")
        self.assertEqual(len(uses), 1)
        self.assertTrue(any("duplicate reference definition" in issue for issue in errors))

    def test_malformed_reference_definition_is_diagnosed(self):
        definitions, usages, errors = scan_reference_links(
            "[Doc][docs]\n[docs]: \n"
        )
        self.assertEqual(definitions, {})
        self.assertEqual(len(usages), 1)
        self.assertTrue(any("malformed reference definition" in error for error in errors))

    def test_code_fences_inline_code_comments_and_footnotes_are_ignored(self):
        doc = (
            "Read [Guide][docs].\n"
            + "\x60[Missing][inline]\x60\n"
            + "~~~~md\n[Missing][fenced]\n[fenced]: gone.md\n"
            + "~~~\n[Still ignored][fenced]\n~~~~\n"
            + "<!-- [Hidden][commented] -->\n"
            + "<!--\n[Hidden][multiline]\n-->\n"
            + "    [Hidden][indented]\n"
            + "[^note]: This is a footnote.\n"
            + "[docs]: <guides/how-to.md#intro> \"Guide\"\n"
        )
        definitions, uses, errors = scan_reference_links(doc)
        self.assertEqual(errors, [])
        self.assertEqual(list(definitions), ["docs"])
        self.assertEqual([u.label for u in uses], ["docs"])

    def test_reference_validation_checks_paths_anchors_and_undefined_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "guides").mkdir()
            (root / "guides/how-to.md").write_text(
                "# Intro\n## Repeat\n## Repeat\n", encoding="utf-8"
            )
            (root / "README.md").write_text(
                "Read [Intro][start], then [duplicate][] and [external][web].\n"
                "[start]: guides/how-to.md#intro\n"
                "[duplicate]: guides/how-to.md#repeat-1\n"
                "[web]: https://example.org/readme\n",
                encoding="utf-8",
            )
            self.assertEqual(validate.validate_markdown_links(root), [])

            (root / "README.md").write_text(
                "[Wrong anchor][start]\n[Unknown][missing]\n"
                "[Bad path][path]\n[Escape][escape]\n"
                "[start]: guides/how-to.md#absent\n"
                "[path]: guides/gone.md\n"
                "[escape]: ../outside.md\n",
                encoding="utf-8",
            )
            problems = validate.validate_markdown_links(root)
            self.assertTrue(any("missing Markdown anchor #absent" in p for p in problems), problems)
            self.assertTrue(any("undefined reference [missing]" in p for p in problems), problems)
            self.assertTrue(any("broken local link" in p for p in problems), problems)
            self.assertTrue(any("link escapes repository" in p for p in problems), problems)

    def test_reference_definition_can_follow_use(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "target.md").write_text("# Target\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[Destination][target]\n[target]: ./target.md\n",
                encoding="utf-8",
            )
            self.assertEqual(validate.validate_markdown_links(root), [])

    def test_duplicate_labels_are_reported_for_real_document(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                "[See][doc]\n[doc]: https://example.org\n[DOC]: https://example.net\n",
                encoding="utf-8",
            )
            problems = validate.validate_markdown_links(root)
            self.assertTrue(any("duplicate reference definition" in p for p in problems), problems)

    def test_no_shortcut_bare_labels_or_footnotes_required(self):
        definitions, uses, errors = scan_reference_links(
            "A mention [not a link] and a footnote[^note].\n"
            "[^note]: explanatory footnote\n"
        )
        self.assertEqual(definitions, {})
        self.assertEqual(uses, [])
        self.assertEqual(errors, [])

    def test_reference_paths_are_not_network_fetched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                "[Info][upstream]\n[upstream]: https://example.invalid/docs\n",
                encoding="utf-8",
            )
            self.assertEqual(validate.validate_markdown_links(root), [])

    def test_prose_line_numbers_are_preserved(self):
        markdown = "First\n~~~\nHidden\n~~~\n[Guide][x]\n[x]: docs.md\n"
        self.assertEqual([line for line, _ in prose_lines(markdown)], [1, 5, 6])


if __name__ == "__main__":
    unittest.main()
