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

- A dependency-free terminal explorer reads the existing JSON catalog and supports searchable JSON output.
- An optional accessible static preview lets readers filter resources without a search server, database or analytics.
- A reproducible single-file HTML snapshot can be opened directly from disk without starting a server; it embeds the reviewed catalog at build time.
- Python and Node tests guard search semantics, browser asset structure, and documentation navigation.
- GitHub Pages deployment remains a separate, explicit decision; no publication workflow is added.

## Later, only if justified

- Consider a separately hosted, searchable documentation site only if local Markdown navigation proves insufficient; assess hosting cost and long-term maintenance first.
- Multilingual guides reviewed by fluent contributors.
- Documented, independently reproducible benchmarks when comparison needs warrant them.
- Richer structured metadata only after concrete use cases emerge.

**Release policy:** No version tags or GitHub Releases for the initial continuously updated knowledge repository. Use ordinary commits and reviewed PRs on `main`.
