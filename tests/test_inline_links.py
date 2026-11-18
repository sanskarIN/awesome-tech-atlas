"""Regression tests for inline Markdown destinations and local references."""

from pathlib import Path
import tempfile
import unittest

from scripts import validate
from scripts.inline_links import scan_inline_links


class InlineMarkdownTests(unittest.TestCase):
    def test_balanced_parentheses_and_images(self):
        line = (
            "Read [chapter](guides/(advanced)/chapter(v2).md) "
            "and ![chart](images/plot(2026).png)"
        )
        self.assertEqual(
            [link.destination for link in scan_inline_links(line)],
            ["guides/(advanced)/chapter(v2).md", "images/plot(2026).png"],
        )

    def test_quoted_and_parenthetical_titles(self):
        cases = (
            ('[Guide](guide.md "long title")', "guide.md"),
            ("[Guide](guide.md 'long title')", "guide.md"),
            ("[Guide](guide.md (nested (parenthetical) title))", "guide.md"),
            ('[Guide](<my guide.md> "title")', "my guide.md"),
            ("[Guide](<guide(v2).md>)", "guide(v2).md"),
        )
        for source, target in cases:
            with self.subTest(source=source):
                self.assertEqual(
                    [x.destination for x in scan_inline_links(source)], [target]
                )

    def test_escaped_destination_punctuation_and_nested_link_text(self):
        line = r"[Text [with \] bracket]](folder/a\(v2\).md) [B](x\#y.md)"
        self.assertEqual(
            [x.destination for x in scan_inline_links(line)],
            ["folder/a(v2).md", "x#y.md"],
        )

    def test_escaped_opening_bracket_is_not_link(self):
        line = r"\[not](bad.md) but [yes](good.md)"
        self.assertEqual(
            [x.destination for x in scan_inline_links(line)], ["good.md"]
        )

    def test_empty_destination_and_multiple_links(self):
        actual = scan_inline_links("[empty]() [one](one.md) [two](two.md)")
        self.assertEqual([x.destination for x in actual], ["", "one.md", "two.md"])
        self.assertEqual([x.column for x in actual], [1, 11, 25])

    def test_malformed_links_not_recognized_as_valid(self):
        examples = (
            "[broken](folder/(unfinished.md)",
            "[broken](<missing-angle.md)",
            '[title without spacing](<file.md>"title")',
            '[unclosed quote](file.md "title)',
            "[undefined][ref]",
            "[shortcut]",
        )
        for example in examples:
            with self.subTest(example=example):
                self.assertEqual(scan_inline_links(example), [])

    def test_local_paths_with_parentheses_spaces_and_anchors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "guides").mkdir()
            (root / "images").mkdir()
            (root / "guides/sample(v2).md").write_text(
                "# Start here\n## Details\n", encoding="utf-8"
            )
            (root / "guides/my guide.md").write_text(
                "# Read me\n", encoding="utf-8"
            )
            (root / "images/plot(2026).png").write_bytes(b"placeholder")
            (root / "README.md").write_text(
                '[Part](guides/sample(v2).md#details "More")\n'
                '[Angle](<guides/my guide.md> "With whitespace")\n'
                '![Plot](images/plot(2026).png)\n'
                '[Encoded](guides/my%20guide.md#read-me)\n'
                '[Escaped](guides/sample\\(v2\\).md#start-here)\n',
                encoding="utf-8",
            )
            self.assertEqual(validate.validate_markdown_links(root), [])

    def test_broken_nested_path_is_found(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                '[Broken](resources/gone(v2).md "Example")\n', encoding="utf-8"
            )
            issues = validate.validate_markdown_links(root)
            self.assertTrue(any("broken local link" in p for p in issues), issues)

    def test_wrong_heading_fragment_is_found(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "details(v2).md").write_text("# There\n", encoding="utf-8")
            (root / "README.md").write_text(
                '[Read](details(v2).md#missing "Details")\n', encoding="utf-8"
            )
            issues = validate.validate_markdown_links(root)
            self.assertTrue(
                any("missing Markdown anchor #missing" in p for p in issues), issues
            )

    def test_inline_code_fences_and_comments_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                "\x60[code](nowhere.md)\x60\n"
                "<!-- [comment](nowhere.md) -->\n"
                "~~~md\n[example](nowhere.md)\n~~~\n"
                "    [indented code](nowhere.md)\n",
                encoding="utf-8",
            )
            self.assertEqual(validate.validate_markdown_links(root), [])

    def test_null_byte_in_decoded_target_is_diagnostic_not_crash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                "[Bad](docs/foo%00bar.md)\n", encoding="utf-8"
            )
            problems = validate.validate_markdown_links(root)
            self.assertTrue(
                any("invalid local path" in p for p in problems), problems
            )

    def test_repository_path_escape_still_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                '[Escaping](../outside(v2).md "Nope")\n', encoding="utf-8"
            )
            problems = validate.validate_markdown_links(root)
            self.assertTrue(
                any("escapes repository" in p for p in problems), problems
            )

    def test_external_url_is_not_fetched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                "[External](https://example.invalid/docs(v2) 'Info')\n",
                encoding="utf-8",
            )
            self.assertEqual(validate.validate_markdown_links(root), [])

    def test_queries_do_not_affect_local_path_resolution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "name(v2).md").write_text("# Valid\n", encoding="utf-8")
            (root / "README.md").write_text(
                '[Document](name(v2).md?lang=en#valid)\n',
                encoding="utf-8",
            )
            self.assertEqual(validate.validate_markdown_links(root), [])


if __name__ == "__main__":
    unittest.main()
