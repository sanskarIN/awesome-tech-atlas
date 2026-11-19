"""Dependency-free provenance and editorial-structure checks for Atlas profiles.

This linter checks local metadata and basic editorial completeness, not the
truth of claims or the current state of any linked upstream project.
"""

from __future__ import annotations

from collections import defaultdict
import re
from typing import Iterator

REQUIRED_FIELDS = ("id", "name", "category", "subcategory", "kind", "url", "verified_on")
SECTIONS = ("Why it matters", "Good fit", "Strength and trade-off", "Try it", "Where to go next")
SOURCE_LABELS = ("Official source", "Original author-published source")
FIELD_RE = re.compile(r"^\*\*(?P<label>[^*\n:]+):\*\*\s*(?P<value>\S.*?)\s*$")
CATEGORY_RE = re.compile(
    r"^\[(?P<label>[^\]\n]+)\]\(\.\./categories/(?P<slug>[a-z0-9-]+)\.md\)"
    r"\s+·\s+(?P<subcategory>.+?)\s*$"
)
FENCE_RE = re.compile(r"^ {0,3}(\x60{3,}|~{3,})")


def visible_markdown_lines(markdown: str) -> Iterator[str]:
    """Ignore fenced example content, with matching delimiters and fence widths."""
    character = ""
    length = 0
    for line in markdown.splitlines():
        marker = FENCE_RE.match(line)
        if not character:
            if marker:
                character, length = marker.group(1)[0], len(marker.group(1))
                continue
            yield line
        elif marker and marker.group(1)[0] == character and len(marker.group(1)) >= length:
            character, length = "", 0


def has_substantive_prose(markdown: str) -> bool:
    """Reject empty/placeholder-only sections without imposing prose uniformity."""
    without_headings = re.sub(r"(?m)^\s{0,3}#{1,6}\s+.*$", "", markdown)
    without_urls = re.sub(r"https?://[^\s)]+", "", without_headings)
    plain = re.sub(r"[*_~#|><\[\]\(\)]", " ", without_urls)
    text = " ".join(plain.split())
    if text.casefold().strip(" .!?-") in {"todo", "tbd", "coming soon", "placeholder"}:
        return False
    return len(re.findall(r"\w", text, re.UNICODE)) >= 20


def validate_profile_content(record: object, markdown: str) -> list[str]:
    """Compare visible profile metadata and narrative structure to one catalog entry."""
    if not isinstance(record, dict) or any(
        not isinstance(record.get(key), str) for key in REQUIRED_FIELDS
    ):
        return ["cannot audit profile until catalog fields have valid string types"]

    errors: list[str] = []
    lines = list(visible_markdown_lines(markdown))
    nonblank = [line.strip() for line in lines if line.strip()]
    expected_title = "# " + record["name"]
    if not nonblank or nonblank[0] != expected_title:
        errors.append(f"profile title mismatch: expected {expected_title!r}")

    headings = [(i, line[3:].strip()) for i, line in enumerate(lines) if line.startswith("## ")]
    header_end = headings[0][0] if headings else len(lines)
    fields: dict[str, list[str]] = defaultdict(list)
    for line in lines[:header_end]:
        match = FIELD_RE.fullmatch(line.strip())
        if match:
            fields[match.group("label")].append(match.group("value").strip())

    def one_field(label: str) -> str | None:
        values = fields.get(label, [])
        if not values:
            errors.append(f"missing profile metadata: {label}")
            return None
        if len(values) > 1:
            errors.append(f"duplicate profile metadata: {label}")
            return None
        return values[0]

    sources = [
        (label, value)
        for label in SOURCE_LABELS for value in fields.get(label, [])
    ]
    if len(sources) != 1:
        errors.append("expected exactly one source metadata line")
    elif sources[0][1] != record["url"]:
        errors.append("source URL mismatch with catalog")

    kind = one_field("Type")
    canonical_kind = record["kind"].replace("-", " ")
    if kind is not None and kind != canonical_kind and not (
        kind.startswith(canonical_kind + " (") and kind.endswith(")")
        and len(kind) > len(canonical_kind) + 3
    ):
        errors.append("resource type mismatch with catalog")

    category = one_field("Category")
    if category is not None:
        parsed = CATEGORY_RE.fullmatch(category)
        if parsed is None:
            errors.append("malformed category metadata link or subcategory")
        else:
            if parsed.group("slug") != record["category"]:
                errors.append("category link mismatch with catalog")
            if parsed.group("subcategory") != record["subcategory"]:
                errors.append("subcategory mismatch with catalog")

    inspected = one_field("Last official-page inspection")
    if inspected is not None and inspected != record["verified_on"]:
        errors.append("inspection date mismatch with catalog")

    positions: dict[str, list[int]] = defaultdict(list)
    for position, heading in headings:
        positions[heading].append(position)
    for heading in SECTIONS:
        matches = positions.get(heading, [])
        if not matches:
            errors.append(f"missing narrative heading: ## {heading}")
            continue
        if len(matches) > 1:
            errors.append(f"duplicate narrative heading: ## {heading}")
            continue
        position = matches[0]
        end = next((i for i, _ in headings if i > position), len(lines))
        body = "\n".join(lines[position + 1:end])
        if not has_substantive_prose(body):
            errors.append(f"empty or insubstantial section: ## {heading}")
        if heading == "Strength and trade-off":
            for label in ("Strength", "Limitation"):
                if not re.search(
                    r"(?m)^\s*-\s+\*\*" + re.escape(label) + r":\*\*",
                    body,
                ):
                    errors.append(f"missing trade-off label: {label}")

    ordered = [positions[heading][0] for heading in SECTIONS if len(positions[heading]) == 1]
    if ordered != sorted(ordered):
        errors.append("narrative headings are out of order")

    statements = [
        match.group("value")
        for line in lines
        if (match := FIELD_RE.fullmatch(line.strip()))
        and match.group("label") == "Verification scope"
    ]
    if len(statements) != 1:
        errors.append("expected exactly one Verification scope statement")
    elif not has_substantive_prose(statements[0]):
        errors.append("Verification scope is empty or insubstantial")
    elif record["verified_on"] not in statements[0]:
        errors.append("Verification scope date mismatch with catalog")
    return errors
