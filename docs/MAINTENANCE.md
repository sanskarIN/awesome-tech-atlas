# Maintenance runbook

Awesome Tech Atlas is continuously updated through reviewed changes on `main`. **Do not create release tags** just for content updates.

## Routine content checks

1. Review new correction issues first. A reported broken upstream URL or misleading fact is more urgent than adding an unrelated entry.
2. Run `python3 scripts/validate.py` locally. This validates metadata, unique identifiers and official URLs, required narrative sections, category and resource index counts against the JSON catalog, **bidirectional membership** (missing, duplicated, misplaced or untracked profiles and category links), index names/subcategories, and internal Markdown file/heading navigation without network requests. Category-page summaries may be shorter or differently worded than catalog summaries; they require editorial review rather than automatic text equality. Profile validation additionally requires a matching title, canonical source URL, type, category/subcategory, inspection date, substantive sections with both strength and limitation, and a dated verification-scope statement. Author-published sources and explanatory type qualifiers remain supported. These structural checks do **not** independently reverify upstream claims or executed examples. When a resource is added, update its category index count and the overall resource total in `resources/README.md`.
3. Run `python3 scripts/atlas.py navigation-audit` to inspect whether curated profiles are linked from learning paths and comparisons, identify untracked profile links, and spot possible editorial coverage gaps. This is a read-only report, **not** a required coverage threshold; resources may properly belong only in their category index. Use `--json`, `--category`, or `--limit` for planning.
4. Run `python3 scripts/atlas.py review-queue --days 90` to prioritize entries whose source was last inspected at least 90 days ago. Use `--category` or `--kind` to narrow the queue, and `--json` for machine-readable planning. This does **not** make HTTP requests, change metadata, or prove a link is broken.
5. Run `python3 -m unittest discover -s tests -v` to check the validator and link-checker regression tests.
6. For upstream link health, run `python3 scripts/check_external_links.py --strict` when network access is available. The scheduled [external-link workflow](../.github/workflows/check-external-links.yml) performs the same check weekly.

The external check tests only the main official URL in each catalog record. A successful HTTP response does not prove that every nested link, feature claim, or release status remains accurate.

Local links to Markdown headings are validated against the target page's GitHub-style heading IDs (including repeated headings). Code fences and inline code samples are ignored. The checker supports standard ATX headings, inline Markdown links and images with balanced URL parentheses, escaped punctuation, angle-delimited paths and optional titles, plus explicit or collapsed reference-style links (`[text][label]`, `[label][]`, with `[label]: destination` definitions). It catches missing or duplicate reference definitions and checks local reference targets and heading fragments. Fenced examples, inline code, indented code and HTML comments do not supply reference definitions. Multiline inline links, shortcut `[label]` references, custom HTML anchors, and complex Markdown extensions still need manual review. Only local paths and fragment anchors are statically checked; remote URLs are not fetched here.

## Inspection-age queue

The review queue calculates days since each catalog `verified_on` date, using the current UTC date by default. A resource exactly at the threshold is included; records are sorted by oldest inspection first, then by name and ID. A `--limit` of 30 applies **after** sorting, and JSON reports the total due before the display limit.

```bash
python3 scripts/atlas.py review-queue --days 90
python3 scripts/atlas.py review-queue --days 180 --category compiler-development --json
python3 scripts/atlas.py review-queue --as-of 2026-11-16 --days 0 --limit 5
```

The `--as-of YYYY-MM-DD` option makes reports reproducible for a chosen UTC calendar date. A date after the chosen `--as-of` date is not due yet. Date thresholds are **editorial reminders, not a guarantee of freshness, link health, or security**. An entry's inspection date must only be updated after a human actually checks its upstream source and relevant claims.

## Triage a failed upstream check

| Observation | Action |
| --- | --- |
| HTTP 200 / successful redirect | Confirm the final destination is still official and relevant if anything changed |
| HTTP 403 / 429 | Treat as **manual review**, not automatic evidence of a dead link; inspect in a browser |
| HTTP 500 / timeout / DNS or TLS issue | Recheck later from a different network before proposing removal |
| HTTP 404 / 410 after HEAD-to-GET retry | Manually confirm; check the official site's new canonical path, then propose a correction |
| Wrong content behind a valid URL | Fix the entry even though the automated HTTP check may pass |

Never automatically delete entries based only on a single network failure. Do not bypass access controls or use third-party mirrors merely to get a green check.

## Confirm a correction

Open the canonical upstream page and inspect the precise claim. Update the profile and `data/resources.json` as needed. Refresh `verified_on` only for entries you actually inspected; document uncertainty in the PR. If a resource is deprecated, make that clear or propose a justified replacement with an alternative.

## Reviewer checklist

- Correct audience and explanation; at least one substantive limitation.
- Upstream source clearly distinguished from editorial judgment.
- No scraped/copyrighted upstream text or imported logos.
- No misleading license claims or unsupported performance comparisons.
- Local validation green; any network warnings explained.
- Relevant GitHub issue linked in the PR when one exists.

## Contributor ownership and scope

Anyone can propose a correction. Maintainers decide what merges; a passing validator is necessary but not sufficient for editorial quality. Prefer a small number of good updates over bulk additions. The roadmap is in [ROADMAP.md](ROADMAP.md).
