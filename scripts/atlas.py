#!/usr/bin/env python3
"""Explore the curated atlas locally, without network requests or dependencies."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date, datetime, timezone
from io import StringIO
import json
from pathlib import Path
import re
import sys
import unicodedata

if __package__:
    from .navigation_audit import NavigationAuditError, navigation_report
else:
    from navigation_audit import NavigationAuditError, navigation_report

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "data" / "resources.json"
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
CSV_COLUMNS = ("id", "name", "category", "subcategory", "kind", "summary", "url", "verified_on")
FORMULA_PREFIX = re.compile(r"^[\s\x00-\x1f]*[=+\-@]")


class CatalogError(ValueError):
    """Raised for invalid local catalog inputs."""


def normalize_text(value: str) -> str:
    """Case-fold, remove combining accents and split punctuation into spaces."""
    decomposed = unicodedata.normalize("NFKD", value).casefold()
    plain = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"\w+", plain))


def load_catalog(path: Path = DEFAULT_CATALOG) -> list[dict[str, str]]:
    try:
        records = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"Cannot read catalog {path}: {exc}") from exc

    if not isinstance(records, list):
        raise CatalogError("Catalog root must be a JSON list.")
    required = ("id", "name", "category", "subcategory", "kind", "summary", "url", "verified_on")
    seen: set[str] = set()
    for index, entry in enumerate(records, 1):
        if not isinstance(entry, dict) or any(
            not isinstance(entry.get(field), str) for field in required
        ):
            raise CatalogError(f"Entry {index}: missing or non-string required field.")
        ident = entry["id"]
        if not SLUG.fullmatch(ident) or ident in seen:
            raise CatalogError(f"Entry {index}: duplicate or invalid id {ident!r}.")
        seen.add(ident)
    return records


def search_records(
    records: list[dict[str, str]],
    query: str = "",
    category: str = "",
    kind: str = "",
    limit: int | None = None,
) -> list[dict[str, str]]:
    """AND-match query terms; rank name matches above summaries and categories."""
    tokens = normalize_text(query).split()
    weights = (
        ("name", 8),
        ("subcategory", 5),
        ("summary", 3),
        ("category", 2),
        ("kind", 1),
    )
    scored = []
    for entry in records:
        if category and entry["category"] != category:
            continue
        if kind and entry["kind"] != kind:
            continue
        fields = [(normalize_text(entry[field]), weight) for field, weight in weights]
        if not all(any(token in text for text, _ in fields) for token in tokens):
            continue
        score = sum(
            max((weight for text, weight in fields if token in text), default=0)
            for token in tokens
        )
        scored.append((score, entry))
    scored.sort(key=lambda item: (-item[0], item[1]["name"].casefold(), item[1]["id"]))
    results = [entry for _, entry in scored]
    return results[:limit] if limit is not None else results


def compare_records(
    records: list[dict[str, str]], ids: list[str],
) -> list[dict[str, str]]:
    """Resolve a shortlist of two or three distinct exact IDs in selection order.

    Reject the entire request on invalid input rather than silently comparing
    a different shortlist. No scores, recommendations or new claims are added.
    """
    if not 2 <= len(ids) <= 3:
        raise CatalogError("Compare requires two or three resource IDs.")
    if len(set(ids)) != len(ids):
        raise CatalogError("Compare requires distinct resource IDs.")
    by_id = {entry["id"]: entry for entry in records}
    missing = [ident for ident in ids if ident not in by_id]
    if missing:
        raise CatalogError("Unknown resource ID(s): " + ", ".join(repr(ident) for ident in missing))
    return [by_id[ident] for ident in ids]


def resources_to_csv(records: list[dict[str, str]]) -> str:
    """Serialize search results with the same columns and formula protections as the browser.

    Return a header even for zero matches. QUOTE_ALL and CRLF mirror site/search.mjs.
    Data is written, never evaluated; formulas are neutralized before spreadsheet import.
    """
    output = StringIO(newline="")
    writer = csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    writer.writerow(CSV_COLUMNS)
    for entry in records:
        writer.writerow([
            "'" + entry[field] if FORMULA_PREFIX.match(entry[field]) else entry[field]
            for field in CSV_COLUMNS
        ])
    return output.getvalue()


def positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("limit must be a positive integer") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("limit must be a positive integer")
    return number


def nonnegative_integer(value: str) -> int:
    """Parse a non-negative inspection-age threshold."""
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("days must be a non-negative integer") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("days must be a non-negative integer")
    return number


def iso_date(value: str) -> date:
    """Parse a strict ISO calendar date for reproducible inspection reports."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must be a valid YYYY-MM-DD day") from exc


def inspection_queue(
    records: list[dict[str, str]],
    as_of: date,
    minimum_age_days: int = 90,
    category: str = "",
    kind: str = "",
) -> list[dict[str, str | int]]:
    """Oldest-inspected entries first; age is not evidence of a broken resource."""
    if minimum_age_days < 0:
        raise ValueError("minimum_age_days must not be negative")
    due: list[dict[str, str | int]] = []
    for entry in records:
        if category and entry["category"] != category:
            continue
        if kind and entry["kind"] != kind:
            continue
        inspected_value = entry["verified_on"]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", inspected_value):
            raise CatalogError(f"{entry['id']}: invalid inspection date {inspected_value!r}")
        try:
            inspected_on = date.fromisoformat(inspected_value)
        except ValueError as exc:
            raise CatalogError(
                f"{entry['id']}: invalid inspection date {inspected_value!r}"
            ) from exc
        age_days = (as_of - inspected_on).days
        if age_days >= minimum_age_days:
            due.append({
                "id": entry["id"],
                "name": entry["name"],
                "category": entry["category"],
                "kind": entry["kind"],
                "verified_on": inspected_value,
                "age_days": age_days,
                "profile": f"resources/{entry['id']}.md",
            })
    due.sort(key=lambda item: (
        -item["age_days"], str(item["name"]).casefold(), str(item["id"]),
    ))
    return due


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search, inspect and summarize the local Awesome Tech Atlas catalog."
    )
    parser.add_argument(
        "--catalog", type=Path, default=DEFAULT_CATALOG,
        help="JSON catalog path (default: data/resources.json)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    search = commands.add_parser("search", help="Search titles, topics, summaries and kinds")
    search.add_argument("query", nargs="?", default="", help="Words to match (AND semantics)")
    search.add_argument("--category", default="", help="Exact category slug")
    search.add_argument("--kind", default="", help="Exact resource kind")
    search.add_argument("--limit", type=positive_integer, default=30)
    output_format = search.add_mutually_exclusive_group()
    output_format.add_argument("--json", action="store_true", help="Machine-readable JSON results")
    output_format.add_argument("--csv", action="store_true", help="Formula-safe CSV (quoted UTF-8, CRLF)")

    show = commands.add_parser("show", help="Inspect one resource by exact ID")
    show.add_argument("id", help="Example: scikit-learn")
    show.add_argument("--json", action="store_true")

    compare = commands.add_parser("compare", help="Compare two or three curated resources by exact ID")
    compare.add_argument("ids", nargs="+", metavar="ID")
    compare.add_argument("--json", action="store_true", help="Ordered array of catalog records")

    for name, description in (
        ("categories", "Show category counts"),
        ("kinds", "Show resource-kind counts"),
        ("stats", "Show summary counts (not freshness or quality scores)"),
    ):
        command = commands.add_parser(name, help=description)
        command.add_argument("--json", action="store_true")
    review = commands.add_parser(
        "review-queue", help="List resources due for human editorial reinspection"
    )
    review.add_argument(
        "--days", type=nonnegative_integer, default=90,
        help="Minimum days since last inspection (inclusive; default: 90)",
    )
    review.add_argument(
        "--as-of", type=iso_date, default=datetime.now(timezone.utc).date(),
        help="UTC calendar date for calculating age (YYYY-MM-DD; default: today UTC)",
    )
    review.add_argument("--category", default="", help="Exact category slug")
    review.add_argument("--kind", default="", help="Exact resource kind")
    review.add_argument("--limit", type=positive_integer, default=30)
    review.add_argument("--json", action="store_true", help="Machine-readable report")
    audit = commands.add_parser(
        "navigation-audit",
        help="Report which curated profiles are linked from guides and comparisons",
    )
    audit.add_argument(
        "--root", type=Path, default=ROOT,
        help="Repository root containing guides/, comparisons/ and resources/",
    )
    audit.add_argument("--category", default="", help="Exact category slug to report")
    audit.add_argument("--limit", type=positive_integer, default=30,
                       help="Maximum unlinked resources to display (default: 30)")
    audit.add_argument("--json", action="store_true",
                       help="Machine-readable full per-resource navigation coverage")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
    except CatalogError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.command == "search":
        output = search_records(catalog, args.query, args.category, args.kind, args.limit)
        if args.json:
            print(json.dumps(output, ensure_ascii=False, indent=2))
        elif args.csv:
            csv_text = resources_to_csv(output)
            # Writing UTF-8 bytes avoids Windows text-mode CRLF doubling in redirected CSV.
            if hasattr(sys.stdout, "buffer"):
                sys.stdout.buffer.write(csv_text.encode("utf-8"))
            else:
                sys.stdout.write(csv_text)
        elif not output:
            print("No matching resources. Try another query or filter.")
        else:
            for item in output:
                print(f"{item['name']} [{item['category']}]")
                print(f"  {item['summary']}")
                print(f"  {item['url']}  |  resources/{item['id']}.md")
        return 0

    if args.command == "show":
        entry = next((item for item in catalog if item["id"] == args.id), None)
        if entry is None:
            print(f"Unknown resource ID: {args.id}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(entry, ensure_ascii=False, indent=2))
        else:
            for field, value in entry.items():
                print(f"{field}: {value}")
            print(f"profile: resources/{entry['id']}.md")
        return 0

    if args.command == "compare":
        try:
            selected = compare_records(catalog, args.ids)
        except CatalogError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(selected, ensure_ascii=False, indent=2))
        else:
            print("Selected resources (in input order; not a ranking):")
            for entry in selected:
                print(f"\n{entry['name']} [{entry['id']}]")
                for field, label in (
                    ("category", "Topic"),
                    ("subcategory", "Subcategory"),
                    ("kind", "Resource type"),
                    ("summary", "Summary"),
                    ("url", "Official source"),
                    ("verified_on", "Last source inspection"),
                ):
                    print(f"  {label}: {entry[field]}")
                print(f"  Curated profile: resources/{entry['id']}.md")
            print("\nInspection dates are not security, performance or quality scores.")
        return 0

    if args.command == "review-queue":
        try:
            due = inspection_queue(
                catalog, args.as_of, args.days, args.category, args.kind,
            )
        except CatalogError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        selected = due[:args.limit]
        if args.json:
            print(json.dumps({
                "as_of": args.as_of.isoformat(),
                "minimum_age_days": args.days,
                "matching_resources": len(due),
                "shown_resources": len(selected),
                "resources": selected,
            }, ensure_ascii=False, indent=2))
        else:
            print(
                f"As of {args.as_of.isoformat()}: {len(due)} resource(s) last "
                f"inspected at least {args.days} day(s) ago "
                f"(showing {len(selected)})."
            )
            for item in selected:
                print(
                    f"  {item['age_days']:>4}d  {item['name']} "
                    f"[{item['category']}]  {item['verified_on']}  {item['profile']}"
                )
            print("Inspection age is a review priority, not proof of a broken link.")
        return 0

    if args.command == "navigation-audit":
        try:
            report = navigation_report(catalog, args.root, args.category)
        except NavigationAuditError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 2
        selected = report["unlinked_resources"][:args.limit]
        report["shown_unlinked"] = len(selected)
        report["unlinked_resources"] = selected
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            docs = report["source_documents"]
            print(
                f"Navigation audit: {docs['guides']} guide document(s), "
                f"{docs['comparisons']} comparison document(s), "
                f"{report['catalog_resources']} catalog resource(s)."
            )
            print(
                f"  In guides: {report['linked_in_guides']}; "
                f"in comparisons: {report['linked_in_comparisons']}; "
                f"in either: {report['linked_in_either']}."
            )
            print(
                f"  Unlinked from these documents: {report['unlinked_total']} "
                f"(showing {len(selected)})."
            )
            for item in selected:
                print(f"  - {item['name']} [{item['category']}] {item['profile']}")
            untracked = report["untracked_profile_links"]
            if untracked:
                print(f"  Untracked profile link(s): {len(untracked)}")
                for link in untracked:
                    print(f"  - {link['source']} -> {link['profile']}")
            print("Editorial link coverage is not a quality or verification score.")
        return 0

    if args.command == "stats":
        payload = {
            "resources": len(catalog),
            "categories": len({entry["category"] for entry in catalog}),
            "kinds": len({entry["kind"] for entry in catalog}),
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            for label, count in payload.items():
                print(f"{label}: {count}")
        return 0

    field = "category" if args.command == "categories" else "kind"
    counts = dict(sorted(Counter(entry[field] for entry in catalog).items()))
    if args.json:
        print(json.dumps(counts, indent=2))
    else:
        for label, count in counts.items():
            print(f"{label}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
