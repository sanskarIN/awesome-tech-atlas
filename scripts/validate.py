#!/usr/bin/env python3
"""Validate the curated catalog and internal Markdown navigation (stdlib only)."""

from __future__ import annotations

from collections import Counter
import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit

if __package__:
    from .reference_links import scan_reference_links, prose_lines
    from .inline_links import scan_inline_links
else:
    from reference_links import scan_reference_links, prose_lines
    from inline_links import scan_inline_links

if __package__:
    from .profile_quality import validate_profile_content
else:
    from profile_quality import validate_profile_content

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


# Inline Markdown destinations are parsed in scripts/inline_links.py.
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
    href = target.strip().strip("<>")
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


FENCE_RE = re.compile(r"^ {0,3}(\x60{3,}|~{3,})")
HEADING_RE = re.compile(r"^ {0,3}#{1,6}(?:\s+|$)(.*?)\s*#*\s*$")
INLINE_CODE_RE = re.compile(r"(\x60+)(.*?)\1")


def active_markdown_lines(content: str):
    """Yield Markdown prose lines, excluding fenced code blocks."""
    fence_char = None
    fence_length = 0
    for line in content.splitlines():
        match = FENCE_RE.match(line)
        if fence_char is None:
            if match:
                fence_char, fence_length = match.group(1)[0], len(match.group(1))
                continue
            yield line
        elif match and match.group(1)[0] == fence_char and len(match.group(1)) >= fence_length:
            fence_char = None


def github_heading_anchors(content: str) -> set[str]:
    """Generate GitHub-style IDs for ATX headings used in this repository."""
    counts: dict[str, int] = {}
    anchors: set[str] = set()
    for line in active_markdown_lines(content):
        match = HEADING_RE.match(line)
        if not match:
            continue
        heading = match.group(1)
        heading = re.sub(r"!?\[([^\]\n]+)\]\([^\)\n]+\)", r"\1", heading)
        heading = html.unescape(re.sub(r"<[^>]*>", "", heading))
        heading = re.sub(r"[\x60*_~]", "", heading)
        base = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        if not base:
            continue
        n = counts.get(base, 0)
        counts[base] = n + 1
        anchors.add(base if n == 0 else f"{base}-{n}")
    return anchors


def validate_markdown_links(root: Path) -> list[str]:
    """Validate ordinary inline and explicit reference-style local Markdown links.

    Link-definition labels are case-insensitive, and references can precede
    their definitions. This is a static check; external hosts are not fetched.
    """
    errors: list[str] = []
    anchor_cache: dict[Path, set[str]] = {}
    root = root.resolve()

    for md in sorted(root.rglob("*.md")):
        if ".git" in md.relative_to(root).parts:
            continue
        content = md.read_text(encoding="utf-8")
        relative = md.relative_to(root)

        def check_target(target: str, context: str = "") -> None:
            href = target.strip()
            if href.startswith("<") and href.endswith(">"):
                href = href[1:-1]
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "tel:")):
                return
            prefix = f"{relative}{context}"
            if "\x00" in unquote(parsed.path):
                errors.append(f"{prefix}: invalid local path (NUL byte): {target}")
                return
            try:
                resolved = md if not parsed.path else resolve_local_link(md, href, root)
            except (ValueError, OSError) as exc:
                errors.append(f"{prefix}: invalid local path {target}: {exc}")
                return
            if resolved is None:
                return
            try:
                rel_target = resolved.relative_to(root)
            except ValueError:
                errors.append(f"{prefix}: link escapes repository: {target}")
                return
            if not resolved.exists():
                errors.append(f"{prefix}: broken local link: {target}")
                return
            if parsed.fragment and resolved.suffix.lower() == ".md":
                anchors = anchor_cache.get(resolved)
                if anchors is None:
                    anchors = github_heading_anchors(resolved.read_text(encoding="utf-8"))
                    anchor_cache[resolved] = anchors
                fragment = unquote(parsed.fragment)
                if fragment not in anchors:
                    errors.append(
                        f"{prefix}: missing Markdown anchor "
                        f"#{fragment} in {rel_target}"
                    )

        for line_number, prose in prose_lines(content):
            for link in scan_inline_links(prose):
                check_target(link.destination, f":{line_number}")

        definitions, usages, syntax_errors = scan_reference_links(content)
        errors.extend(f"{relative}: {problem}" for problem in syntax_errors)
        for definition in definitions.values():
            check_target(definition.destination, f":{definition.line}")
        for usage in usages:
            if usage.label not in definitions:
                errors.append(
                    f"{relative}:{usage.line}: undefined reference [{usage.label}]"
                )
    return errors


CATEGORY_INDEX_ROW_RE = re.compile(
    r"^\|\s*\[[^]\n]+\]\((?P<slug>[a-z0-9-]+)\.md\)\s*\|\s*(?P<count>\d+)\s*\|$"
)
RESOURCE_COUNT_RE = re.compile(r"\*\*(\d+) upstream-inspected starter resources\*\*")


def validate_index_counts(root: Path, records: list[object]) -> list[str]:
    """Ensure static category and resource totals agree with the catalog.

    Only valid category strings contribute to individual category counts;
    other malformed records are reported by the main catalog validator.
    """
    errors: list[str] = []
    category_counts = Counter(
        record["category"]
        for record in records
        if isinstance(record, dict)
        and isinstance(record.get("category"), str)
        and record["category"] in CATEGORIES
    )
    category_index = root / "categories/README.md"
    if category_index.is_file():
        displayed: dict[str, int] = {}
        for line in category_index.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| ["):
                continue
            match = CATEGORY_INDEX_ROW_RE.fullmatch(line.strip())
            if match is None:
                errors.append(f"Category index has malformed row: {line}")
                continue
            slug = match.group("slug")
            if slug not in CATEGORIES:
                errors.append(f"Category index lists unknown category: {slug}")
            elif slug in displayed:
                errors.append(f"Category index duplicates category: {slug}")
            else:
                displayed[slug] = int(match.group("count"))
        for slug in sorted(CATEGORIES):
            if slug not in displayed:
                errors.append(f"Category index missing category: {slug}")
            elif displayed[slug] != category_counts[slug]:
                errors.append(
                    f"Category index count mismatch for {slug}: "
                    f"shows {displayed[slug]}, catalog has {category_counts[slug]}"
                )

    resource_index = root / "resources/README.md"
    if resource_index.is_file():
        match = RESOURCE_COUNT_RE.search(resource_index.read_text(encoding="utf-8"))
        if match is None:
            errors.append("Resource index missing its declared resource total.")
        elif int(match.group(1)) != len(records):
            errors.append(
                f"Resource index count mismatch: "
                f"shows {match.group(1)}, catalog has {len(records)}"
            )
    return errors


RESOURCE_INDEX_ENTRY_RE = re.compile(
    r"^\|\s*\[(?P<name>[^\]\n]+)\]\((?P<id>[a-z0-9-]+)\.md\)\s*"
    r"\|\s*(?P<subcategory>[^|\n]+?)\s*"
    r"\|\s*\[[^\]\n]+\]\(\.\./categories/(?P<category>[a-z0-9-]+)\.md\)\s*\|\s*$"
)
CATEGORY_RESOURCE_ENTRY_RE = re.compile(
    r"^\s*-\s+\*\*\[(?P<name>[^\]\n]+)\]"
    r"\(\.\./resources/(?P<id>[a-z0-9-]+)\.md\):\*\*\s+.+$"
)


def validate_index_membership(root: Path, records: list[object]) -> list[str]:
    """Check both directions of catalog, indexes and profile membership.

    A category's prose may deliberately differ from a catalog summary, but
    resource identity and placement must not drift. Malformed records are
    diagnosed by validate_repository; exclude them here to avoid crashing.
    """
    errors: list[str] = []
    catalog = {
        record["id"]: record
        for record in records
        if isinstance(record, dict)
        and is_valid_slug(record.get("id"))
        and all(
            isinstance(record.get(field), str)
            for field in ("name", "subcategory", "category")
        )
        and record["category"] in CATEGORIES
    }

    index = root / "resources" / "README.md"
    if index.is_file():
        seen: Counter[str] = Counter()
        for line in active_markdown_lines(index.read_text(encoding="utf-8")):
            if not line.startswith("| ["):
                continue
            match = RESOURCE_INDEX_ENTRY_RE.fullmatch(line.strip())
            if match is None:
                errors.append(f"Resource index has malformed entry row: {line}")
                continue
            ident = match.group("id")
            seen[ident] += 1
            record = catalog.get(ident)
            if record is None:
                errors.append(f"Resource index lists unknown resource: {ident}")
                continue
            for field in ("name", "subcategory", "category"):
                actual = match.group(field).strip()
                if actual != record[field]:
                    errors.append(
                        f"Resource index {ident}: {field} mismatch "
                        f"(index {actual!r}, catalog {record[field]!r})"
                    )
        for ident in sorted(catalog):
            if not seen[ident]:
                errors.append(f"Resource index missing catalog entry: {ident}")
        for ident, count in sorted(seen.items()):
            if count > 1:
                errors.append(f"Resource index duplicates resource: {ident} ({count} rows)")

    resources = root / "resources"
    if resources.is_dir():
        for path in sorted(resources.glob("*.md")):
            if path.name != "README.md" and path.stem not in catalog:
                errors.append(f"Uncataloged resource profile: resources/{path.name}")

    categories = root / "categories"
    if categories.is_dir():
        for path in sorted(categories.glob("*.md")):
            if path.name != "README.md" and path.stem not in CATEGORIES:
                errors.append(f"Unrecognized category page: categories/{path.name}")

    for category in sorted(CATEGORIES):
        page = categories / f"{category}.md"
        if not page.is_file():
            continue  # Already reported by the required-category file check.
        seen: Counter[str] = Counter()
        for line in active_markdown_lines(page.read_text(encoding="utf-8")):
            if not line.lstrip().startswith("- **["):
                continue
            match = CATEGORY_RESOURCE_ENTRY_RE.fullmatch(line)
            if match is None:
                errors.append(f"Category {category}: malformed resource row: {line}")
                continue
            ident = match.group("id")
            seen[ident] += 1
            record = catalog.get(ident)
            if record is None:
                errors.append(f"Category {category}: unknown resource: {ident}")
                continue
            if record["category"] != category:
                errors.append(
                    f"Category {category}: misplaced resource {ident}; "
                    f"catalog assigns it to {record['category']}"
                )
            if match.group("name") != record["name"]:
                errors.append(f"Category {category}: name mismatch for {ident}")
        for ident, record in sorted(catalog.items()):
            if record["category"] == category and not seen[ident]:
                errors.append(f"Category {category}: missing catalog resource {ident}")
        for ident, count in sorted(seen.items()):
            if count > 1:
                errors.append(
                    f"Category {category}: duplicate resource {ident} ({count} rows)"
                )
    return errors


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

        if not isinstance(record["category"], str) or record["category"] not in CATEGORIES:
            errors.append(f"{resource_id}: unknown category: {record['category']!r}")
        if not isinstance(record["kind"], str) or record["kind"] not in KINDS:
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
        errors.extend(
            f"{resource_id}: {problem}"
            for problem in validate_profile_content(record, content)
        )
        for heading in HEADINGS:
            if heading not in content:
                errors.append(f"{resource_id}: missing profile heading {heading}")
        for heading in missing_worked_example_headings(content):
            errors.append(f"{resource_id}: worked example missing {heading}")
        if not isinstance(url, str) or url not in content:
            errors.append(f"{resource_id}: official URL missing from profile")
        if not isinstance(record["verified_on"], str) or record["verified_on"] not in content:
            errors.append(f"{resource_id}: inspection date missing from profile")

        category = record["category"]
        if isinstance(category, str) and category in CATEGORIES:
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

    errors.extend(validate_index_counts(root, records))
    errors.extend(validate_index_membership(root, records))
    errors.extend(validate_markdown_links(root))

    return errors


def main() -> int:
    problems = validate_repository()
    if problems:
        for problem in problems:
            print("ERROR:", problem, file=sys.stderr)
        print(f"FAILED with {len(problems)} error(s).", file=sys.stderr)
        return 1
    count = len(json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8")))
    print(f"PASS: {count} entries; {len(CATEGORIES)} categories; indexes, profile metadata, editorial structure and local links valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
