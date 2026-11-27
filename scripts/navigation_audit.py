"""Offline editorial navigation coverage for curated Atlas resources.

Reports where profiles are mentioned in guides/comparisons. Being mentioned
is not evidence of correctness, freshness, importance, or resource quality.
No links are fetched and no repository files are modified.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

if __package__:
    from .inline_links import scan_inline_links
    from .reference_links import prose_lines, scan_reference_links
else:
    from inline_links import scan_inline_links
    from reference_links import prose_lines, scan_reference_links


class NavigationAuditError(ValueError):
    """The chosen documentation root cannot be audited reliably."""


def _profile_id(source: Path, destination: str, root: Path) -> str | None:
    """Resolve only a *direct* link to a resource profile under this root."""
    try:
        parsed = urlsplit(destination)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return None
        local = unquote(parsed.path)
        if "\x00" in local or local.startswith("/"):
            return None
        path = (source.parent / local).resolve()
        resource_dir = (root / "resources").resolve()
        if path.parent != resource_dir or path.suffix.lower() != ".md":
            return None
        return path.stem
    except (ValueError, OSError):
        return None


def _document_links(source: Path, root: Path) -> set[str]:
    """Collect unique profile IDs per document from inline/reference links."""
    try:
        markdown = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise NavigationAuditError(f"Cannot read {source}: {exc}") from exc

    definitions, usages, errors = scan_reference_links(markdown)
    if errors:
        raise NavigationAuditError(
            f"Cannot audit {source}: invalid reference definitions: "
            + "; ".join(errors)
        )

    destinations = [
        item.destination
        for _, line in prose_lines(markdown)
        for item in scan_inline_links(line)
    ]
    destinations.extend(
        definitions[usage.label].destination
        for usage in usages if usage.label in definitions
    )
    return {
        ident for destination in destinations
        if (ident := _profile_id(source, destination, root)) is not None
    }


def navigation_report(
    records: list[dict[str, str]],
    root: Path,
    category: str = "",
) -> dict[str, object]:
    """Build a deterministic per-resource editorial navigation report.

    Resource IDs link to the known catalog; untracked links are reported
    separately. Multiple mentions of one resource in a single document
    count only once. A category filter narrows resources, not scanned docs.
    """
    root = root.resolve()
    documents: dict[str, list[Path]] = {
        "guides": sorted((root / "guides").glob("*.md")),
        "comparisons": sorted((root / "comparisons").glob("*.md")),
    }
    if not any(documents.values()):
        raise NavigationAuditError(
            f"No guides/*.md or comparisons/*.md documents under {root}"
        )

    ids = {record["id"] for record in records}
    mentions: dict[str, dict[str, set[str]]] = {
        ident: {"guides": set(), "comparisons": set()} for ident in ids
    }
    untracked: set[tuple[str, str]] = set()

    for section, paths in documents.items():
        for path in paths:
            source = path.relative_to(root).as_posix()
            for ident in _document_links(path, root):
                if ident in ids:
                    mentions[ident][section].add(source)
                else:
                    untracked.add((source, f"resources/{ident}.md"))

    filtered = [
        record for record in records
        if not category or record["category"] == category
    ]
    filtered.sort(key=lambda record: (record["name"].casefold(), record["id"]))

    resources: list[dict[str, object]] = []
    for record in filtered:
        ident = record["id"]
        sources = mentions[ident]
        resources.append({
            "id": ident,
            "name": record["name"],
            "category": record["category"],
            "profile": f"resources/{ident}.md",
            "guides": sorted(sources["guides"]),
            "comparisons": sorted(sources["comparisons"]),
        })

    by_category: dict[str, dict[str, int]] = defaultdict(
        lambda: {"resources": 0, "in_guides": 0, "in_comparisons": 0, "in_either": 0}
    )
    for resource in resources:
        counts = by_category[str(resource["category"])]
        has_guides = bool(resource["guides"])
        has_comparisons = bool(resource["comparisons"])
        counts["resources"] += 1
        counts["in_guides"] += int(has_guides)
        counts["in_comparisons"] += int(has_comparisons)
        counts["in_either"] += int(has_guides or has_comparisons)

    unlinked = [
        {"id": item["id"], "name": item["name"], "category": item["category"],
         "profile": item["profile"]}
        for item in resources
        if not item["guides"] and not item["comparisons"]
    ]
    return {
        "scope": "editorial navigation only; not a resource quality or verification score",
        "category_filter": category or None,
        "source_documents": {key: len(paths) for key, paths in documents.items()},
        "catalog_resources": len(resources),
        "linked_in_guides": sum(bool(item["guides"]) for item in resources),
        "linked_in_comparisons": sum(bool(item["comparisons"]) for item in resources),
        "linked_in_either": len(resources) - len(unlinked),
        "unlinked_total": len(unlinked),
        "unlinked_resources": unlinked,
        "categories": [
            {"category": key, **by_category[key]}
            for key in sorted(by_category)
        ],
        "resources": resources,
        "untracked_profile_links": [
            {"source": source, "profile": profile}
            for source, profile in sorted(untracked)
        ],
    }


def profile_references(
    records: list[dict[str, str]], ident: str, root: Path,
) -> dict[str, object]:
    """Find actual outgoing and incoming links between curated profiles.

    Scan every catalogued profile so incoming links are complete within the
    supported Markdown syntax. Do not infer similarity, fetch upstream URLs,
    or silently omit missing or unreadable profiles.
    """
    by_id = {record["id"]: record for record in records}
    if ident not in by_id:
        raise NavigationAuditError(f"Unknown resource ID: {ident!r}")
    root = root.resolve()
    links: dict[str, set[str]] = {}
    for resource_id in sorted(by_id):
        source = root / "resources" / f"{resource_id}.md"
        try:
            resolved = source.resolve(strict=True)
            if resolved != source or not resolved.is_file():
                raise NavigationAuditError(
                    f"Not a regular profile at its expected path: {source}"
                )
        except (OSError, RuntimeError) as exc:
            raise NavigationAuditError(f"Cannot resolve profile {source}: {exc}") from exc
        links[resource_id] = _document_links(source, root) - {resource_id}

    def describe(resource_ids: set[str]) -> list[dict[str, str]]:
        return [
            {"id": key, "name": by_id[key]["name"],
             "category": by_id[key]["category"], "profile": f"resources/{key}.md"}
            for key in sorted(resource_ids, key=lambda k: (by_id[k]["name"].casefold(), k))
        ]

    outgoing = links[ident]
    incoming = {key for key, targets in links.items() if ident in targets}
    return {
        "scope": "explicit profile cross-references; not inferred recommendations",
        "resource": describe({ident})[0],
        "scanned_profiles": len(links),
        "outgoing": describe(outgoing.intersection(by_id)),
        "incoming": describe(incoming),
        "untracked_outgoing": sorted(outgoing.difference(by_id)),
    }
