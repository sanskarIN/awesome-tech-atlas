"""Regression tests for catalog and Markdown quality gates."""

import unittest
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

    def test_local_link_resolution(self):
        root = Path("/tmp/atlas-test")
        source = root / "categories" / "programming-languages.md"
        result = validate.resolve_local_link(source, "../resources/python.md", root)
        self.assertEqual(result, root / "resources" / "python.md")
        self.assertIsNone(validate.resolve_local_link(source, "https://example.com", root))
        self.assertIsNone(validate.resolve_local_link(source, "#overview", root))


if __name__ == "__main__":
    unittest.main()
