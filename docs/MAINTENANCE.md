# Maintenance runbook

Awesome Tech Atlas is continuously updated through reviewed changes on `main`. **Do not create release tags** just for content updates.

## Routine content checks

1. Review new correction issues first. A reported broken upstream URL or misleading fact is more urgent than adding an unrelated entry.
2. Run `python3 scripts/validate.py` locally. This validates metadata, unique identifiers and official URLs, required narrative sections, and internal Markdown file/heading navigation without network requests.
3. Run `python3 -m unittest discover -s tests -v` to check the validator and link-checker regression tests.
4. For upstream link health, run `python3 scripts/check_external_links.py --strict` when network access is available. The scheduled [external-link workflow](../.github/workflows/check-external-links.yml) performs the same check weekly.

The external check tests only the main official URL in each catalog record. A successful HTTP response does not prove that every nested link, feature claim, or release status remains accurate.

Local links to Markdown headings are validated against the target page's GitHub-style heading IDs (including repeated headings). Code fences and inline code samples are ignored. The checker supports standard ATX headings and ordinary inline Markdown links; if a document relies on custom HTML anchors or complex Markdown constructs, verify that navigation manually.

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
