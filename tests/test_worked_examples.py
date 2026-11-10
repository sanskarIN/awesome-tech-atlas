"""Static safeguards for reviewed Markdown walkthroughs.

Intentionally compile, but do not execute, code from Markdown in CI:
third-party PRs must not turn a documentation preview into an execution path.
"""

import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "python": "python",
    "scikit-learn": "python",
    "rust": "rust",
    "react": "jsx",
    "owasp-cheatsheets": "python",
    "sqlite": "python",
    "numpy": "python",
}
HEADINGS = (
    "### Prerequisites",
    "### Steps",
    "### Expected result",
    "### Troubleshooting",
    "### Evidence and execution status",
)


def example_section(resource_id: str) -> str:
    """Extract exactly one worked-example section from a profile."""
    profile = (ROOT / "resources" / f"{resource_id}.md").read_text(encoding="utf-8")
    sections = re.findall(
        r"^## Worked example:[^\n]*\n(.*?)(?=^## |\Z)",
        profile,
        re.MULTILINE | re.DOTALL,
    )
    if len(sections) != 1:
        raise ValueError(f"{resource_id}: expected exactly one worked example")
    return sections[0]


def fenced_code(section: str, language: str) -> str:
    """Pick the intended original code sample, not its expected text output."""
    matches = re.findall(
        rf"^~~~{re.escape(language)}[ \t]*\n(.*?)^~~~[ \t]*$",
        section,
        re.MULTILINE | re.DOTALL,
    )
    if len(matches) != 1:
        raise ValueError(f"expected one {language} code fence, got {len(matches)}")
    return matches[0]


class WorkedExampleTests(unittest.TestCase):
    def test_expected_examples_have_reproducibility_context(self):
        for resource_id, language in EXAMPLES.items():
            with self.subTest(resource=resource_id):
                section = example_section(resource_id)
                positions = [section.find(h) for h in HEADINGS]
                self.assertTrue(all(p >= 0 for p in positions))
                self.assertEqual(positions, sorted(positions))
                self.assertTrue(fenced_code(section, language).strip())
                expected = section.split("### Expected result", 1)[1].split(
                    "### Troubleshooting", 1
                )[0]
                self.assertTrue(expected.strip())
                self.assertIn("https://", section)
                self.assertTrue(
                    "**Executed locally:**" in section
                    or "**Not runtime-tested here:**" in section
                )

    def test_python_snippets_parse_without_execution(self):
        for resource_id, language in EXAMPLES.items():
            if language != "python":
                continue
            with self.subTest(resource=resource_id):
                source = fenced_code(example_section(resource_id), language)
                compile(source, f"{resource_id}.py", "exec")


if __name__ == "__main__":
    unittest.main()
