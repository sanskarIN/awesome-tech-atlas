"""Contract tests: filling contributor template must produce a validator-ready profile.

An author should not have to reverse-engineer internal validation rules to
contribute a well-formed Markdown resource. This suite checks the documented
skeleton against the same linter used for actual catalog entries.
"""

from datetime import date
import json
from pathlib import Path
import re
import unittest

from scripts import validate
from scripts.profile_quality import validate_profile_content

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "docs/RESOURCE_TEMPLATE.md"
REPLACEMENTS = {
    "id": "sample-guide",
    "name": "Sample language guide",
    "category_slug": "programming-languages",
    "category_label": "Programming languages",
    "subcategory": "Language tooling examples",
    "kind_slug": "official-guide",
    "kind_label": "official guide",
    "url": "https://example.org/docs",
    "verified_on": "2026-11-08",
    "summary": "An original, descriptive guide for a small example language and related tooling.",
    "purpose": "A maintained guide can help learners understand basic language tooling.",
    "use_cases": "An introductory use case is understanding the interface before installation.",
    "strength": "It provides an organized starting point for an evidence-backed review.",
    "limitation": "Its examples may not match every runtime and must be checked locally.",
    "first_step": "Read the official introduction and write down the required environment.",
    "alternative_name": "Python documentation",
    "alternative_id": "python",
    "alternative_decision": "Choose the alternative when Python language guidance is needed.",
    "scope_note": "Runtime behavior, installation and specific licensing were not tested.",
    "category_summary": "An original introductory source for language-tooling questions.",
}


def render(text: str) -> str:
    for field, replacement in REPLACEMENTS.items():
        text = text.replace("{{" + field + "}}", replacement)
    return text


def extract_fence(language: str) -> str:
    document = PATH.read_text(encoding="utf-8")
    match = re.search(
        r"(?m)^~~~" + re.escape(language) + r"[ \t]*\n(.*?)^~~~[ \t]*$",
        document,
        re.DOTALL | re.MULTILINE,
    )
    if not match:
        raise ValueError(f"template missing first {language!r} fence")
    return match.group(1)


class ResourceTemplateContractTests(unittest.TestCase):
    def test_copyable_profile_satisfies_real_profile_linter(self):
        source = render(extract_fence("markdown"))
        record = {
            key: REPLACEMENTS[key if key not in {"category", "kind"} else key + "_slug"]
            for key in ("id", "name", "category", "subcategory", "kind", "url", "verified_on")
        }
        self.assertNotRegex(source, r"\{\{[^}]+\}\}")
        self.assertEqual(validate_profile_content(record, source), [])
        self.assertFalse(any(heading not in source for heading in validate.HEADINGS))
        self.assertEqual(validate.missing_worked_example_headings(source), [])

    def test_profile_metadata_defects_are_not_silently_tolerated(self):
        source = render(extract_fence("markdown"))
        record = {
            "id": "sample-guide",
            "name": REPLACEMENTS["name"],
            "category": "programming-languages",
            "subcategory": REPLACEMENTS["subcategory"],
            "kind": "official-guide",
            "url": REPLACEMENTS["url"],
            "verified_on": REPLACEMENTS["verified_on"],
        }
        tests = [
            ("**Official source:**", "**Official documentation:**", "source metadata"),
            ("**Type:**", "**Kind:**", "missing profile metadata: Type"),
            ("## Strength and trade-off", "## Trade-offs", "missing narrative heading"),
            ("**Last official-page inspection:**", "**Last source inspection:**",
             "missing profile metadata: Last official-page inspection"),
        ]
        for original, replacement, expected in tests:
            with self.subTest(metadata=original):
                errors = validate_profile_content(record, source.replace(original, replacement))
                self.assertTrue(
                    any(expected in error for error in errors), errors
                )

    def test_catalog_example_matches_required_json_fields(self):
        catalog = json.loads(render(extract_fence("json")))
        self.assertEqual(set(catalog), validate.FIELDS)
        self.assertEqual(catalog["name"], REPLACEMENTS["name"])
        self.assertEqual(catalog["category"], REPLACEMENTS["category_slug"])
        self.assertEqual(catalog["kind"], "official-guide")
        self.assertTrue(validate.is_clean_official_url(catalog["url"]))
        self.assertTrue(validate.valid_inspection_date(catalog["verified_on"], date(2026, 11, 18)))

    def test_index_row_shapes_match_real_membership_validator(self):
        examples = render(extract_fence("text")).splitlines()
        self.assertEqual(len(examples), 2)
        index = validate.RESOURCE_INDEX_ENTRY_RE.fullmatch(examples[0])
        category = validate.CATEGORY_RESOURCE_ENTRY_RE.fullmatch(examples[1])
        self.assertIsNotNone(index)
        self.assertIsNotNone(category)
        self.assertEqual(index.group("id"), REPLACEMENTS["id"])
        self.assertEqual(index.group("name"), REPLACEMENTS["name"])
        self.assertEqual(index.group("subcategory"), REPLACEMENTS["subcategory"])
        self.assertEqual(index.group("category"), REPLACEMENTS["category_slug"])
        self.assertEqual(category.group("id"), REPLACEMENTS["id"])

    def test_optional_worked_example_contract_has_all_required_subheadings(self):
        document = PATH.read_text(encoding="utf-8")
        self.assertIn("## Worked example:", document)
        for heading in validate.WORKED_EXAMPLE_HEADINGS:
            self.assertIn(heading, document)

    def test_contributing_uses_current_section_and_indexing_contract(self):
        guide = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("**Strength and trade-off**", guide)
        self.assertIn("**Update the maintained indexes manually:**", guide)
        self.assertIn("verification scope", guide)
        self.assertNotIn("The category index is built from the catalog", guide)

    def test_template_explains_source_and_date_are_human_verified(self):
        guide = PATH.read_text(encoding="utf-8")
        self.assertIn("upstream documentation yourself", guide)
        self.assertIn("Never claim to have installed", guide)
        self.assertIn("not", guide.lower())
        self.assertIn("inspection date", guide.lower())


if __name__ == "__main__":
    unittest.main()
