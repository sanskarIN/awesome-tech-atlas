"""Static quality checks for the original applied engineering labs.

Do not execute code extracted from Markdown: external contributors may edit
guide text. Compile Python snippets only, and inspect the remaining code as
documentation rather than running an untrusted build, browser or debugger.
"""

from pathlib import Path
import json
import re
import unittest

from scripts import validate

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "guides" / "applied-engineering-labs.md"
LABS = (
    ("Lab 1: Validate untrusted records with TypeScript", "typescript", "typescript"),
    ("Lab 2: Trace a C logic defect with CMake and GDB", "c", "gdb"),
    ("Lab 3: Review a local form for accessible interaction", "html", "wai-tutorials"),
    ("Lab 4: Scan a tiny language with Python", "python", "crafting-interpreters"),
)
EXPECTED_PROFILES = {
    "typescript", "gdb", "cmake-tutorial", "wai-tutorials",
    "mdn-learn", "crafting-interpreters", "llvm",
}
FENCE_RE = re.compile(
    r"^~~~(?P<language>[a-z0-9+-]+)\s*\n(?P<body>.*?)^~~~[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


def read_guide() -> str:
    return GUIDE.read_text(encoding="utf-8")


def labs() -> dict[str, str]:
    content = read_guide()
    sections: dict[str, str] = {}
    for heading, _, _ in LABS:
        marker = f"## {heading}\n"
        if content.count(marker) != 1:
            raise ValueError(f"expected one {marker.strip()}")
        start = content.index(marker) + len(marker)
        after = content.find("\n## ", start)
        sections[heading] = content[start:after if after != -1 else None]
    return sections


class AppliedLabsTests(unittest.TestCase):
    def test_each_lab_has_reproducible_evidence_sections(self):
        for heading, _, _ in LABS:
            with self.subTest(lab=heading):
                section = labs()[heading]
                sections = (
                    "### Goal and prerequisites", "### Steps",
                    "### Expected result and diagnostic cases",
                    "### Evidence and limitations",
                )
                places = [section.find(label) for label in sections]
                self.assertTrue(all(place >= 0 for place in places), places)
                self.assertEqual(places, sorted(places))
                self.assertIn("Execution status:", section)

    def test_labs_have_expected_original_code_languages(self):
        for heading, language, _ in LABS:
            with self.subTest(lab=heading):
                blocks = list(FENCE_RE.finditer(labs()[heading]))
                self.assertIn(language, [block.group("language") for block in blocks])
                self.assertTrue(
                    all(block.group("body").strip() for block in blocks)
                )

    def test_all_profile_links_resolve_to_catalog(self):
        catalog = json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8"))
        identifiers = {item["id"] for item in catalog}
        links = set(re.findall(r"\.\./resources/([a-z0-9-]+)\.md", read_guide()))
        self.assertTrue(EXPECTED_PROFILES <= links)
        self.assertEqual(links - identifiers, set())

    def test_scanner_example_has_valid_python_syntax_but_is_not_executed(self):
        section = labs()["Lab 4: Scan a tiny language with Python"]
        snippets = [
            block.group("body") for block in FENCE_RE.finditer(section)
            if block.group("language") == "python"
        ]
        self.assertEqual(len(snippets), 1)
        compile(snippets[0], "documented_scanner.py", "exec")
        self.assertIn("unexpected character", snippets[0])
        self.assertIn("match.start()", snippets[0])
        self.assertIn('kind = "LET"', snippets[0])

    def test_typescript_example_has_runtime_checks_not_only_type_casts(self):
        section = labs()["Lab 1: Validate untrusted records with TypeScript"]
        self.assertIn("value: unknown", section)
        self.assertIn("typeof value", section)
        self.assertIn("Number.isSafeInteger", section)
        self.assertIn("JSON.stringify", section)
        self.assertIn("not a runtime validator", section.lower())

    def test_debugging_lab_contains_before_after_expectations(self):
        section = labs()["Lab 2: Trace a C logic defect with CMake and GDB"]
        self.assertIn("observed=10 expected=15", section)
        self.assertIn("observed=15 expected=15", section)
        self.assertIn("value < last", section)
        self.assertIn("value <= last", section)
        self.assertIn("CMAKE_BUILD_TYPE=Debug", section)
        self.assertIn("multi-configuration", section)

    def test_accessibility_lab_is_explicit_about_limits(self):
        section = labs()["Lab 3: Review a local form for accessible interaction"]
        self.assertIn('for="topic"', section)
        self.assertIn('aria-describedby="topic-help"', section)
        self.assertIn('role="status"', section)
        self.assertIn("textContent", section)
        self.assertIn("not a WCAG conformance audit", section)

    def test_guide_heading_anchors_present(self):
        content = read_guide()
        anchors = validate.github_heading_anchors(content)
        for heading, _, _ in LABS:
            slug = re.sub(r"[^a-z0-9\- ]", "", heading.casefold()).replace(" ", "-")
            self.assertIn(slug, anchors)

    def test_primary_navigation_points_to_labs(self):
        for path in (
            ROOT / "README.md",
            ROOT / "guides/learning-paths.md",
            ROOT / "guides/project-based-tracks.md",
        ):
            with self.subTest(path=path.name):
                self.assertIn("applied-engineering-labs.md",
                              path.read_text(encoding="utf-8"))

    def test_lab_scopes_do_not_claim_unobserved_execution(self):
        for heading, _, _ in LABS:
            with self.subTest(heading=heading):
                section = labs()[heading]
                self.assertIn("Execution status:", section)
                self.assertIn("not", section.lower())


if __name__ == "__main__":
    unittest.main()
