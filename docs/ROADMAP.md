# Roadmap: quality gates before scale

This roadmap is a **direction**, not a release schedule or promise.

## Foundation

- Accessible README, contributor guidelines, policy, issue and PR templates.
- A small set of upstream-inspected entries with real limitations.
- Local catalog validation and an automated CI check.

## Depth

- Add reproducible, original walkthroughs and more entry-specific caveats.
- Improve coverage of gaps based on community needs, not quotas.
- Expand cross-referenced comparison pages and learning paths.
- Audit accessibility, sources, and documentation drift.

## Local-first tooling

- A dependency-free terminal explorer reads the existing JSON catalog, supports searchable JSON output, and compares two or three exact resource IDs with deterministic selection order and optional JSON output.
- An optional accessible static preview lets readers filter resources without a search server, database or analytics.
- A reproducible single-file HTML snapshot can be opened directly from disk without starting a server; it embeds the reviewed catalog and all original curated Markdown profiles at build time.
- Python and Node tests guard search semantics, browser asset structure, and documentation navigation. Technical keywords such as C++ retain their punctuation, and real-catalog parity tests cover result ordering and CSV export across runtimes.
- Local and offline browsers allow up to three resources to be compared using existing catalog metadata; HTTP pages support shareable comparison query parameters without tracking or saved browsing history.
- The local and Pages explorers read curated Markdown profiles on demand from same-origin files, with safe plain-text rendering and download support; offline snapshots use embedded profiles without a network request.
- An opt-in GitHub Pages workflow builds a verified, project-path-aware artifact and deploys only after checks pass on protected `main`; setup and post-deploy verification are documented in [the Pages runbook](PAGES.md).

## Later, only if justified

- Consider a richer documentation site only if existing Markdown navigation and the static Pages explorer prove insufficient; assess maintenance and accessibility first.
- Multilingual guides reviewed by fluent contributors.
- Documented, independently reproducible benchmarks when comparison needs warrant them.
- Richer structured metadata only after concrete use cases emerge.

**Release policy:** No version tags or GitHub Releases for the initial continuously updated knowledge repository. Use ordinary commits and reviewed PRs on `main`.
