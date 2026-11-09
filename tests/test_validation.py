"""Regression tests for catalog and Markdown quality gates."""

import unittest
import tempfile
from datetime import date
from pathlib import Path

from scripts import validate


class ValidatorTests(unittest.TestCase):
    def test_current_repository_is_valid(self):
        self.assertEqual(validate.validate_repository(validate.ROOT), [])

    def test_slug_rules(self):
        self.assertTrue(validate.is_valid_slug("scikit-learn"))
        for bad in ("", "../invalid", "UpperCase", "a--b", "a_b"):
            with self.subTest(bad=bad):
                self.assertFalse(validate.is_valid_slug(bad))

    def test_official_url_requires_clean_https(self):
        self.assertTrue(validate.is_clean_official_url("https://docs.python.org/3/"))
        for bad in (
            "http://example.com",
            "https://example.com/?utm_source=spam",
            "https://example.com/#section",
            "https://user:pass@example.com/",
            " javascript:alert(1)",
        ):
            with self.subTest(bad=bad):
                self.assertFalse(validate.is_clean_official_url(bad))

    def test_date_must_be_valid_and_not_future(self):
        today = date(2026, 11, 8)
        self.assertTrue(validate.valid_inspection_date("2026-11-08", today))
        self.assertFalse(validate.valid_inspection_date("2026-11-09", today))
        self.assertFalse(validate.valid_inspection_date("2026-13-01", today))
        self.assertFalse(validate.valid_inspection_date("11/08/2026", today))

    def test_optional_worked_example_headings(self):
        self.assertEqual(validate.missing_worked_example_headings("## Try it"), [])
        self.assertEqual(
            validate.missing_worked_example_headings("## Worked example: incomplete"),
            list(validate.WORKED_EXAMPLE_HEADINGS),
        )
        complete = "## Worked example: example\n" + "\n".join(
            validate.WORKED_EXAMPLE_HEADINGS
        )
        self.assertEqual(validate.missing_worked_example_headings(complete), [])
        self.assertEqual(
            validate.missing_worked_example_headings(
                complete.replace("### Troubleshooting", "")
            ),
            ["### Troubleshooting"],
        )

    def test_markdown_heading_ids(self):
        content = (
            "# Intro: Start\n"
            "## Repeat\n"
            "## Repeat\n"
            "## **Bold** and \x60Code\x60\n"
            "~~~markdown\n"
            "## Fenced example is not a heading\n"
            "~~~\n"
        )
        self.assertEqual(
            validate.github_heading_anchors(content),
            {"intro-start", "repeat", "repeat-1", "bold-and-code"},
        )

    def test_markdown_link_anchors_and_code_fences(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "guides").mkdir()
            (root / "guides" / "topic.md").write_text(
                "# Topic\n## Repeat\n## Repeat\n", encoding="utf-8"
            )
            (root / "README.md").write_text(
                "# Start\n"
                "[same-page](#start)\n"
                "[relative](guides/topic.md#repeat-1)\n"
                "\x60[ignored inline](#does-not-exist)\x60\n"
                "~~~markdown\n"
                "[ignored fenced](#does-not-exist)\n"
                "~~~\n",
                encoding="utf-8",
            )
            self.assertEqual(validate.validate_markdown_links(root), [])

            (root / "README.md").write_text(
                "[bad fragment](guides/topic.md#missing)\n"
                "[bad path](guides/nope.md)\n"
                "[escape](../outside.md)\n",
                encoding="utf-8",
            )
            problems = validate.validate_markdown_links(root)
            self.assertEqual(len(problems), 3)
            self.assertTrue(any("missing Markdown anchor #missing" in p for p in problems))
            self.assertTrue(any("broken local link" in p for p in problems))
            self.assertTrue(any("link escapes repository" in p for p in problems))

    def test_local_link_resolution(self):
        root = Path("/tmp/atlas-test")
        source = root / "categories" / "programming-languages.md"
        result = validate.resolve_local_link(source, "../resources/python.md", root)
        self.assertEqual(result, root / "resources" / "python.md")
        self.assertIsNone(validate.resolve_local_link(source, "https://example.com", root))
        self.assertIsNone(validate.resolve_local_link(source, "#overview", root))


if __name__ == "__main__":
    unittest.main()
