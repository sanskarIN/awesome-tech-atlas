# Contributing to Awesome Tech Atlas

Thank you for making this atlas more accurate and useful. Contributions of **corrections, context, resources, examples, comparisons, and accessibility improvements** are welcome.

## Before proposing an entry

1. Search [the catalog](data/resources.json), existing [resource profiles](resources/README.md), issues, and PRs to avoid duplicates.
2. Check that the upstream documentation is official and currently accessible; avoid shorteners, tracking URLs, affiliate links, personal referral links, and unverified downloads.
3. Read the upstream material yourself. Describe its documented purpose accurately without copying its text.
4. Explain **why it earns a place**: audience, typical use case, first practical step, and one honest limitation.
5. Distinguish factual statements, editorial analysis, and information that has not been checked.
6. Confirm that any quoted snippet, image, or embedded code can legally be reused. Prefer your own small illustrative example.

**One focused topic per PR** is ideal. Big contributions are welcome when organized and independently verifiable, but bulk lists of uninspected entries will not be merged.

## Add a resource

1. Add one record to [`data/resources.json`](data/resources.json). Use a unique lowercase hyphenated `id`, an existing `category`, the canonical official `url`, a concise `summary`, and `verified_on` (YYYY-MM-DD) **only after checking that page**.
2. Create `resources/<id>.md` based on [the profile template](docs/RESOURCE_TEMPLATE.md) with **Why it matters**, **Good fit**, **Trade-offs**, **Try it**, and **Where to go next**.
3. The category index is built from the catalog. If creating a new category, explain the need in an issue first, then update [the category index](categories/README.md) and the validation script's allowed-category set.
4. Run `python3 scripts/validate.py` (Python 3.10+; no packages needed). When available, also check external links with `python3 scripts/check_external_links.py`. Fix real failures; explain network false positives.
5. Open a PR with a short summary, the official source used, what was actually checked, and any unresolved uncertainty.

### Update or correct an entry

Make the smallest evidence-backed change. If a URL redirects, update it to the canonical official destination where reasonable. Refresh `verified_on` **only for resources whose official page you personally rechecked**. If capabilities or licensing vary by release or distribution, say so rather than asserting one universal fact.

### Quality bars

- Original writing; no copied paragraphs, scraped data dumps, or marketing-only descriptions.
- Plain language, descriptive link names, usable heading order, accessible tables.
- No unverified numerical benchmarks, unsupported "best" rankings, or claims of security assurance.
- No link-only PRs, duplicate projects under different names, abandoned resources disguised as actively maintained, or affiliate placements.
- Examples must be short, correct for their stated context, and safe. State required setup if any.
- Treat AI-assisted contributions like other contributions: **verify each factual claim and link** yourself.

## Pull requests and protected main

The default branch `main` is protected by the active repository ruleset **Protect main**. Routine changes must use a pull request, pass the **Catalog, Markdown, and tests** status check, and resolve review threads. Force pushes and deletion of the protected branch are blocked. The current ruleset does **not** require a minimum number of approving reviews; reviewers are still encouraged for substantive changes.

See the [branch-protection and recovery runbook](docs/BRANCH_PROTECTION.md) for the verified configuration, self-review limitations, and steps for handling a blocked check. GitHub settings are authoritative if the ruleset changes.

## Review process

Maintainers review usefulness, correctness, evidence, readability, source licensing, and scope. Changes may be requested; acceptance is not automatic. An official link check date means **the URL and relevant documentation were reviewed**, not that all listed software has been installed, security-tested, or independently benchmarked.

For potentially sensitive security concerns, consult [SECURITY.md](SECURITY.md) rather than publishing details in a public issue. For conduct concerns, see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

All original contributions to this repository are submitted under **[CC0 1.0 Universal](LICENSE)**. Contributors must have the right to submit their text, and upstream materials keep their own licenses.
