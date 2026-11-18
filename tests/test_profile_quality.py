"""Regression tests for profile provenance and non-placeholder narratives."""

import json
from pathlib import Path
import unittest

from scripts.profile_quality import (
    has_substantive_prose, validate_profile_content, visible_markdown_lines,
)

ROOT = Path(__file__).resolve().parents[1]
ENTRY = {
    "id": "sample-docs",
    "name": "Sample documentation",
    "category": "programming-languages",
    "subcategory": "Sample language",
    "kind": "official-docs",
    "url": "https://example.org/docs",
    "verified_on": "2026-11-08",
}
PROFILE = """# Sample documentation

**Official source:** https://example.org/docs
**Type:** official docs
**Category:** [Programming languages](../categories/programming-languages.md) · Sample language
**Last official-page inspection:** 2026-11-08

## Why it matters

A carefully explained language reference with upstream examples and terminology.

## Good fit

Learning the core language and finding precise explanations before coding.

## Strength and trade-off

- **Strength:** The reference groups related language features clearly.
- **Limitation:** The examples cannot replace testing in your own context.

## Try it

Read an introductory section and reproduce a short example in a local file.

## Where to go next

- Read the upstream reference, then compare another documented resource.

**Verification scope:** The official documentation page was inspected on 2026-11-08; examples were not executed.
"""


class ProfileQualityTests(unittest.TestCase):
    def assert_problem(self, content, fragment, entry=ENTRY):
        problems = validate_profile_content(entry, content)
        self.assertTrue(any(fragment in problem for problem in problems), problems)

    def test_clean_fixture_passes(self):
        self.assertEqual(validate_profile_content(ENTRY, PROFILE), [])

    def test_all_real_profiles_match_current_catalog(self):
        records = json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8"))
        for record in records:
            with self.subTest(resource=record["id"]):
                content = (ROOT / "resources" / (record["id"] + ".md")).read_text(
                    encoding="utf-8"
                )
                self.assertEqual(validate_profile_content(record, content), [])

    def test_author_published_source_and_explanatory_type_are_allowed(self):
        content = PROFILE.replace(
            "**Official source:**", "**Original author-published source:**"
        ).replace("**Type:** official docs", "**Type:** official docs (upstream source)")
        self.assertEqual(validate_profile_content(ENTRY, content), [])

    def test_source_url_must_match_header_not_just_body(self):
        content = PROFILE.replace(
            "**Official source:** https://example.org/docs",
            "**Official source:** https://example.org/old"
        )
        content += "\nThe canonical URL https://example.org/docs also occurs in prose.\n"
        self.assertIn("https://example.org/docs", content)
        self.assert_problem(content, "source URL mismatch")

    def test_duplicate_source_labels_are_rejected(self):
        content = PROFILE.replace(
            "**Type:** official docs",
            "**Original author-published source:** https://example.org/docs\n**Type:** official docs",
        )
        self.assert_problem(content, "exactly one source")

    def test_wrong_title_is_rejected(self):
        self.assert_problem(PROFILE.replace("# Sample documentation", "# Other docs", 1), "title mismatch")

    def test_type_mismatch_is_rejected(self):
        self.assert_problem(
            PROFILE.replace("**Type:** official docs", "**Type:** official guide"),
            "type mismatch",
        )

    def test_type_annotation_must_not_hide_wrong_kind(self):
        self.assert_problem(
            PROFILE.replace("**Type:** official docs", "**Type:** official guide (other)"),
            "type mismatch",
        )

    def test_category_link_mismatch_is_rejected(self):
        self.assert_problem(
            PROFILE.replace("categories/programming-languages.md", "categories/developer-tools.md"),
            "category link mismatch",
        )

    def test_subcategory_mismatch_is_rejected(self):
        self.assert_problem(
            PROFILE.replace(" · Sample language", " · Different language"),
            "subcategory mismatch",
        )

    def test_date_mismatch_is_rejected_in_header(self):
        self.assert_problem(
            PROFILE.replace(
                "**Last official-page inspection:** 2026-11-08",
                "**Last official-page inspection:** 2026-11-07",
            ),
            "inspection date mismatch",
        )

    def test_date_mismatch_is_rejected_in_scope(self):
        self.assert_problem(
            PROFILE.replace(
                "inspected on 2026-11-08", "inspected on 2026-11-07"
            ),
            "Verification scope date mismatch",
        )

    def test_missing_metadata_is_rejected(self):
        self.assert_problem(
            PROFILE.replace("**Category:** [Programming languages](../categories/programming-languages.md) · Sample language\n", ""),
            "missing profile metadata: Category",
        )

    def test_duplicate_metadata_is_rejected(self):
        content = PROFILE.replace(
            "**Type:** official docs", "**Type:** official docs\n**Type:** official docs"
        )
        self.assert_problem(content, "duplicate profile metadata: Type")

    def test_empty_narrative_is_rejected(self):
        self.assert_problem(
            PROFILE.replace(
                "Learning the core language and finding precise explanations before coding.",
                "TODO",
            ),
            "empty or insubstantial section: ## Good fit",
        )

    def test_missing_narrative_heading_is_rejected(self):
        self.assert_problem(
            PROFILE.replace("## Try it", "## Try something"),
            "missing narrative heading: ## Try it",
        )

    def test_repeated_narrative_heading_is_rejected(self):
        self.assert_problem(
            PROFILE.replace("## Good fit", "## Good fit\n## Good fit", 1),
            "duplicate narrative heading: ## Good fit",
        )

    def test_out_of_order_narrative_headings_are_rejected(self):
        content = PROFILE.replace("## Good fit", "## Wrong").replace(
            "## Try it", "## Good fit"
        ).replace("## Wrong", "## Try it")
        self.assert_problem(content, "out of order")

    def test_trade_off_requires_both_strength_and_limitation(self):
        self.assert_problem(
            PROFILE.replace("- **Limitation:**", "- **Concern:**"),
            "missing trade-off label: Limitation",
        )
        self.assert_problem(
            PROFILE.replace("- **Strength:**", "- **Positive:**"),
            "missing trade-off label: Strength",
        )

    def test_missing_verification_scope_is_rejected(self):
        self.assert_problem(PROFILE.replace("**Verification scope:**", "**Review note:**"), "Verification scope statement")

    def test_code_fence_cannot_forge_a_heading_or_metadata_line(self):
        content = PROFILE.replace("## Good fit", "## Good enough", 1)
        content += "\n~~~md\n## Good fit\n~~~\n"
        self.assert_problem(content, "missing narrative heading: ## Good fit")
        content = PROFILE.replace("**Official source:**", "**Unverified URL:**", 1)
        content += "\n~~~md\n**Official source:** https://example.org/docs\n~~~\n"
        self.assert_problem(content, "exactly one source")

    def test_fence_tracking_respects_delimiter_width(self):
        sample = "Start\n" + "~" * 4 + "md\nHidden\n" + "~" * 3 + "\nStill hidden\n" + "~" * 4 + "\nEnd\n"
        self.assertEqual(list(visible_markdown_lines(sample)), ["Start", "End"])

    def test_malformed_record_types_dont_crash_linter(self):
        invalid = dict(ENTRY, verified_on=[])
        self.assertIn("catalog fields", " ".join(validate_profile_content(invalid, PROFILE)))

    def test_prose_detection_rejects_placeholders_without_rejecting_real_lists(self):
        self.assertFalse(has_substantive_prose("TODO"))
        self.assertFalse(has_substantive_prose("## heading\n"))
        self.assertTrue(has_substantive_prose("- A concrete example that documents how this capability is used."))


if __name__ == "__main__":
    unittest.main()
