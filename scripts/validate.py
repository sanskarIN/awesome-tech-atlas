#!/usr/bin/env python3
"""Validate the curated catalog and internal Markdown navigation (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "programming-languages",
    "computer-science-fundamentals",
    "artificial-intelligence-machine-learning",
    "deep-learning-neural-networks",
    "software-engineering",
    "systems-programming",
    "compiler-development",
    "operating-systems",
    "databases-storage",
    "developer-tools",
    "web-development",
    "mobile-desktop-development",
    "scientific-computing",
    "algorithms-data-structures",
    "computer-architecture",
    "networking-distributed-systems",
    "cybersecurity-secure-engineering",
    "cloud-computing-devops",
    "open-source-projects-communities",
}
KINDS = {
    "official-docs",
    "official-guide",
    "learning-course",
    "learning-guide",
    "reference",
    "specification",
    "community-reference",
    "community-guide",
}
FIELDS = {"id", "name", "category", "subcategory", "kind", "url", "summary", "verified_on"}
REQUIRED_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE",
    "SECURITY.md",
    "categories/README.md",
    "resources/README.md",
    "data/resources.json",
    "docs/EDITORIAL_POLICY.md",
    "docs/RESOURCE_TEMPLATE.md",
    "guides/learning-paths.md",
    "comparisons/README.md",
}
HEADINGS = (
    "## Why it matters",
    "## Good fit",
    "## Strength and trade-off",
    "## Try it",
    "## Where to go next",
)
WORKED_EXAMPLE_HEADINGS = (
    "### Prerequisites",
    "### Steps",
    "### Expected result",
    "### Troubleshooting",
    "### Evidence and execution status",
)


def missing_worked_example_headings(content: str) -> list[str]:
    """Require reproducibility context when a profile opts into a worked example."""
    if "## Worked example" not in content:
        return []
    return [heading for heading in WORKED_EXAMPLE_HEADINGS if heading not in content]


LINK_RE = re.compile(r"!?(?:\[[^\]\n]*\])\(([^)\n]+)\)")
SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


def is_valid_slug(value: object) -> bool:
    return isinstance(value, str) and bool(SLUG_RE.fullmatch(value))


def is_clean_official_url(value: object) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    parsed = urlsplit(value)
    return (
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
        and not any(c.isspace() for c in value)
    )


def valid_inspection_date(value: object, today: date | None = None) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        day = date.fromisoformat(value)
    except ValueError:
        return False
    return day <= (today or date.today())


def resolve_local_link(source: Path, target: str, root: Path) -> Path | None:
    """Return resolved local path; None for external links and same-page anchors."""
    href = target.strip().split(" ", 1)[0].strip("<>")
    if href.startswith(("#", "mailto:", "tel:")):
        return None
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        return None
    local = unquote(parsed.path)
    if not local:
        return None
    if local.startswith("/"):
        # Absolute website paths are not valid repository-relative links.
        return root.parent / "__invalid_absolute_link__"
    return (source.parent / local).resolve()


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for name in sorted(REQUIRED_FILES):
        if not (root / name).is_file():
            errors.append(f"Missing required file: {name}")
    catalog_path = root / "data/resources.json"
    if not catalog_path.is_file():
        return errors
    try:
        records = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return errors + [f"Invalid catalog JSON: {exc}"]
    if not isinstance(records, list) or not records:
        return errors + ["Catalog must be a non-empty JSON list."]

    ids: set[str] = set()
    names: set[str] = set()
    urls: set[str] = set()
    for index, record in enumerate(records, 1):
        tag = f"Entry {index}"
        if not isinstance(record, dict):
            errors.append(f"{tag} must be an object.")
            continue
        missing = FIELDS - record.keys()
        extra = record.keys() - FIELDS
        if missing:
            errors.append(f"{tag} is missing: {sorted(missing)}")
        if extra:
            errors.append(f"{tag} has unsupported fields: {sorted(extra)}")
        if missing:
            continue

        resource_id = record["id"]
        if not is_valid_slug(resource_id):
            errors.append(f"{tag} has invalid id: {resource_id!r}")
            continue
        if resource_id in ids:
            errors.append(f"Duplicate resource id: {resource_id}")
        ids.add(resource_id)

        name = record["name"]
        if not isinstance(name, str) or len(name.strip()) < 3:
            errors.append(f"{resource_id}: name must be descriptive.")
        else:
            folded = name.casefold().strip()
            if folded in names:
                errors.append(f"Duplicate resource name: {name}")
            names.add(folded)

        if record["category"] not in CATEGORIES:
            errors.append(f"{resource_id}: unknown category: {record['category']!r}")
        if record["kind"] not in KINDS:
            errors.append(f"{resource_id}: unknown kind: {record['kind']!r}")
        for field in ("subcategory", "summary"):
            value = record[field]
            if not isinstance(value, str) or len(value.strip()) < (8 if field == "subcategory" else 40):
                errors.append(f"{resource_id}: {field} is too short or not text.")

        url = record["url"]
        if not is_clean_official_url(url):
            errors.append(f"{resource_id}: URL must be an HTTPS official page without queries/fragments.")
        else:
            normalized = url.rstrip("/").casefold()
            if normalized in urls:
                errors.append(f"Duplicate official URL: {url}")
            urls.add(normalized)
        if not valid_inspection_date(record["verified_on"]):
            errors.append(f"{resource_id}: invalid or future inspection date: {record['verified_on']}")

        profile = root / "resources" / f"{resource_id}.md"
        if not profile.is_file():
            errors.append(f"{resource_id}: profile missing at {profile.relative_to(root)}")
            continue
        content = profile.read_text(encoding="utf-8")
        for heading in HEADINGS:
            if heading not in content:
                errors.append(f"{resource_id}: missing profile heading {heading}")
        for heading in missing_worked_example_headings(content):
            errors.append(f"{resource_id}: worked example missing {heading}")
        if url not in content:
            errors.append(f"{resource_id}: official URL missing from profile")
        if record["verified_on"] not in content:
            errors.append(f"{resource_id}: inspection date missing from profile")

        category = record["category"]
        catpath = root / "categories" / f"{category}.md"
        if not catpath.is_file():
            errors.append(f"{resource_id}: category page missing: {category}.md")
        elif f"../resources/{resource_id}.md" not in catpath.read_text(encoding="utf-8"):
            errors.append(f"{resource_id}: missing category page backlink")

    index = (root / "resources/README.md")
    if index.is_file():
        body = index.read_text(encoding="utf-8")
        for resource_id in ids:
            if f"({resource_id}.md)" not in body:
                errors.append(f"Index missing profile: {resource_id}")
    for category in CATEGORIES:
        if not (root / "categories" / f"{category}.md").is_file():
            errors.append(f"Missing category page: {category}.md")

    # Test links without network: external links are handled separately.
    for md in sorted(root.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1)
            resolved = resolve_local_link(md, target, root)
            if resolved is None:
                continue
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{md.relative_to(root)}: link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{md.relative_to(root)}: broken local link: {target}")

    return errors


def main() -> int:
    problems = validate_repository()
    if problems:
        for problem in problems:
            print("ERROR:", problem, file=sys.stderr)
        print(f"FAILED with {len(problems)} error(s).", file=sys.stderr)
        return 1
    count = len(json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8")))
    print(f"PASS: {count} catalog entries; {len(CATEGORIES)} categories; local Markdown links valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
