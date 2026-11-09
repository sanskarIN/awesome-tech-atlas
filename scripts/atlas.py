#!/usr/bin/env python3
"""Explore the curated atlas locally, without network requests or dependencies."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "data" / "resources.json"
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")


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


def positive_integer(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("limit must be a positive integer") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("limit must be a positive integer")
    return number


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
    search.add_argument("--json", action="store_true", help="Machine-readable results")

    show = commands.add_parser("show", help="Inspect one resource by exact ID")
    show.add_argument("id", help="Example: scikit-learn")
    show.add_argument("--json", action="store_true")

    for name, description in (
        ("categories", "Show category counts"),
        ("kinds", "Show resource-kind counts"),
        ("stats", "Show summary counts (not freshness or quality scores)"),
    ):
        command = commands.add_parser(name, help=description)
        command.add_argument("--json", action="store_true")
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
