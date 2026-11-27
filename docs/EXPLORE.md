# Explore the atlas locally

Awesome Tech Atlas has three optional, **dependency-light** ways to browse the same curated `data/resources.json` file: a Python terminal explorer, a locally served static browser, and a generated single-file offline snapshot. All three local commands are read-only: none edits the catalog, collects analytics, needs a database, or deploys GitHub Pages. A separate, opt-in GitHub Actions workflow can publish a validated static artifact after the repository's Pages setting is configured.

The original [Markdown resource index](../resources/README.md) remains the primary, durable source. Every resource still needs a human-reviewed profile and an upstream reference.

## Option A: Search from a terminal

Requires **Python 3.10+** and only the standard library. From the repository root:

```bash
python3 scripts/atlas.py stats
python3 scripts/atlas.py categories
python3 scripts/atlas.py kinds
python3 scripts/atlas.py search rust
python3 scripts/atlas.py search "C++" --category programming-languages
python3 scripts/atlas.py search cpp-msvc
python3 scripts/atlas.py search "machine learning" --limit 8
python3 scripts/atlas.py search database --category databases-storage --json
python3 scripts/atlas.py search rust --csv > rust-resources.csv
python3 scripts/atlas.py search "machine learning" --limit 8 --csv > ml-resources.csv
python3 scripts/atlas.py show scikit-learn
python3 scripts/atlas.py profile scikit-learn
python3 scripts/atlas.py profile scikit-learn > scikit-learn-profile.md
python3 scripts/atlas.py compare rust python go-docs
python3 scripts/atlas.py compare sqlite postgresql --json
python3 scripts/atlas.py related python
python3 scripts/atlas.py related rust --json
python3 scripts/atlas.py review-queue --days 90
python3 scripts/atlas.py review-queue --days 180 --category compiler-development --json
python3 scripts/atlas.py navigation-audit
python3 scripts/atlas.py navigation-audit --category compiler-development --json
```

On Windows, use `py -3` instead of `python3` if that is your configured launcher.

Search uses **AND** semantics for terms, ignores case and most combining accents, and ranks title matches over summary matches. Resource IDs are searchable too (for example, `cpp-msvc`). Punctuation in `C++` and `C#` is preserved; these and single-character queries match complete tokens rather than arbitrary substrings. An entry mentioning both C and C++ may still match both queries. Other terms continue to support substring matching. Tied search scores are ordered by lowercase resource title in Unicode code-point order, then by ID, rather than browser locale. This is a simple technical-keyword search, not a full multilingual collation or stemming engine. Category and kind filters use exact catalog identifiers (see `categories` and `kinds`). `--json` emits an array of complete catalog records for `search`, or the selected record for `show`. For `search`, `--csv` emits the **same columns and match order as the browser's CSV exporter**, with quoted UTF-8 cells, CRLF rows, and a leading apostrophe on formula-like values to prevent spreadsheet evaluation. Use either `--json` or `--csv`, not both. `--csv` prints a header even when there are zero matches, so pipelines can handle empty results consistently. The CLI writes raw UTF-8 without a byte-order mark; the browser adds a UTF-8 BOM to its downloaded CSV for spreadsheet compatibility. Treat formula safety as a defensive export measure, not a substitute for reviewing untrusted source data. No results is not a command error; unknown resource IDs produce a nonzero exit status.

`profile ID` reads the complete original curated Markdown file, rather than only its catalog metadata. IDs are exact and case-sensitive. The command reads UTF-8 locally and writes the original bytes, including existing line endings, to standard output; it does not render Markdown, execute snippets, or fetch upstream links. Redirect the output to a file **outside the source profile path** to save a copy. Unknown IDs, missing files, invalid UTF-8, and symlinked profile paths fail with a nonzero exit status and no partial profile output. The default profile root is this repository; for a custom fixture use `--catalog path/to/catalog.json profile ID --root path/to/repository` (the root must contain `resources/`). This is not a source reinspection and does not update catalog dates.

`compare` accepts two or three distinct, case-sensitive resource IDs. It displays the selected entries in the supplied order, including the same curated summaries, official sources, inspection dates and profile paths used by the browser. Add `--json` to emit an ordered array of the original catalog records for a local pipeline. Duplicate IDs, unknown IDs and selections outside the two-to-three range fail with a nonzero exit code and no partial result. Unlike the browser's forgiving URL restoration, the explicit terminal command rejects invalid selections so scripts cannot silently compare a different set. The output is read-only and not a ranking, benchmark or recommendation; consult the linked profiles for limitations.

`related ID` reports curated profiles directly linked from the selected profile and profiles that link back to it. The command scans all catalogued profiles locally, deduplicates links, excludes self-links and separates uncatalogued outgoing IDs. It uses the same single-line inline and explicit reference-style Markdown parsing as `navigation-audit`; fenced code, inline code and HTML comments are excluded. External links, ambiguous shortcut references and multiline inline links are outside its scope. Results are ordered by resource name (case-folded), then ID. Use `--json` for the full directional report, or `--root path/to/repository` with a custom catalog to inspect another tree. Unknown IDs, missing, unreadable or symlinked catalog profiles fail rather than silently returning incomplete backlinks. Empty link lists are valid. These are **explicit editorial connections**, not similarity scores, endorsements or a claim that the upstream resource was recently inspected. No external requests or repository edits occur.

To prioritize editorial reinspection, `review-queue` sorts entries by their `verified_on` date (oldest first) and selects those at least `--days` old, with an inclusive threshold. The default is 90 days as of the current **UTC** date; `--as-of YYYY-MM-DD` allows deterministic reports, and `--category`, `--kind`, `--limit`, and `--json` control the output. The JSON report includes total matches **before** the display limit. This is a read-only planning aid: an old inspection date does not mean an entry is broken. See the [maintenance runbook](MAINTENANCE.md#inspection-age-queue).

`navigation-audit` checks which catalog profiles are directly linked from `guides/*.md` and `comparisons/*.md`, including explicit reference-style Markdown links. It counts each document's mention once, reports category coverage and resources not mentioned in either collection, and flags direct links to profiles absent from the catalog. Use `--json` for per-resource source-document paths, `--category` for a narrower set, `--limit` to shorten the unlinked list, or `--root path/to/repository` for an alternate tree. **This is editorial navigation coverage, not a resource-quality score or a requirement that every item appear in every learning path.** The command reads existing files only and does not fetch external links.

To test against a different JSON file, put `--catalog path/to/resources.json` *before* the command. The complete catalog is still validated by `python3 scripts/validate.py` before contributions are merged.

## Option B: Open the interactive resource browser

The browser interface lives under `site/`. It has no npm install step, no framework, no backend and no network-based search API.

1. Clone the repository and open a terminal at its root.
2. Run a local HTTP server:

   ```bash
   python3 -m http.server 8000 --bind 127.0.0.1
   ```

3. Open <http://127.0.0.1:8000/site/> in your browser.
4. Search by keywords, filter by topic and resource type, and open the profile or official upstream source.

**Important:** Do not double-click `site/index.html` using a `file://` URL. Browsers commonly prevent `fetch` of the neighboring JSON file in that context. Start the local server from the **repository root**, not from `site/`, so `../data/resources.json` resolves correctly. Stop the server with Ctrl+C when finished.

The interface provides visible labels, a keyboard skip link, dark-mode and reduced-motion support, and a live result count. Use **Add to comparison** on up to three catalog cards to see a side-by-side table of existing topics, subcategories, summaries, official sources, profile links, and recorded source-inspection dates. Each selection is reversible with **Remove** or **Clear comparison**. Comparisons are a personal shortlist, **not a ranking, benchmark, or recommendation**; the table adds no new factual claims. Selections persist when search filters change. When served over HTTP, the `compare` URL parameter makes a shortlist shareable; unknown, repeated and excessive resource IDs are ignored. Comparison IDs are not stored in cookies or browser storage. **Download matching results CSV** saves only the current search/filter matches, in display order, with titles, topics, official URLs, and inspection dates; it makes no network request. CSV fields are quoted, and formula-like values are prefixed to prevent spreadsheet interpretation. Press **/** (outside form fields) to focus search; press **Escape** while typing in search to clear it. Filter state is stored only in the page URL query parameters so it can be shared. No cookies, local-storage history, third-party fonts, trackers, account login, or service worker are used.

**When JavaScript is disabled**, use the Markdown catalog link on the page. **When catalog loading fails**, the explorer reveals a direct link to the local Markdown resource index, which can also be opened from disk. The interactive interface is an enhancement, not the only way to discover resources.

The local search page loads only files from your own server. Clicking a **resource name** reads the curated Markdown profile directly from the local `resources/` directory into an accessible plain-text dialog (no Markdown-to-HTML execution). The dialog lets you download the Markdown and provides a separate **View on GitHub** link. The same reader works from the hosted GitHub Pages site, and comparison-table profile links open it too. Embedded offline profiles use the same reader without network requests. Opening a resource name in a new tab follows its direct local Markdown URL; if an in-page profile request fails, the dialog reports the problem and leaves the GitHub link available, without automatically contacting a third-party site. Clicking **official source** opens the upstream website, which requires connectivity and has its own privacy and licensing policies. An inspection date is a documentation-review marker, **not** a runtime, performance, maintenance, or security guarantee.

## Option C: Build a fully offline searchable HTML file

No JavaScript package installation, database, or hosted web server is required. With Python 3.10+ available, run from the **repository root**:

```bash
python3 scripts/build_offline.py
```

On Windows, use `py -3 scripts/build_offline.py`. The command generates:

```text
dist/awesome-tech-atlas-offline.html
```

Double-click that file to open it with a modern browser. The HTML includes the catalog JSON, **all currently curated original resource profiles**, local search/filter code, and styles in **one file**. Search, category filters, kind filters, a **Download snapshot JSON** button, and **Download matching results CSV** work even with your network disconnected.

- Select a resource title to open its complete profile in the shared read-only dialog. The profile is deliberately displayed as **plain Markdown text**, preserving examples, links, headings, and code exactly rather than attempting an incomplete or unsafe Markdown renderer.
- Use **Download Markdown** in the dialog to save the original profile locally. Press **Escape** or **Close** to return to the search results.
- The **View on GitHub** and **Official source** links still open external websites if network access is available.
- With JavaScript disabled, the generated HTML contains an offline expandable resource index with each complete profile as escaped plain text, not just a summary.

The exporter fails if a catalog profile is missing or its official URL disagrees with the catalog. Catalog data and Markdown profiles are embedded without creating new editorial content or updating source inspection dates.

The result is a snapshot of the catalog at build time. **Rebuild it after changing resource data.** Files under `dist/` are ignored by Git and should not be committed automatically. To choose a destination:

```bash
python3 scripts/build_offline.py --output my-offline-atlas.html
```

**Offline comparison:** The same three-resource table and removal controls work in the standalone HTML snapshot, with **Read offline profile** available from the comparison table. Because `file://` browsers handle history inconsistently, comparison state stays in the current open page only and is not written to the file URL.

**Offline limits:** The embedded curated profiles can be read, searched by catalog metadata, and saved without internet. Links to GitHub, official upstream manuals, and other external pages still need connectivity. Profile text is shown as Markdown source rather than formatted HTML; snippets are documentation, not executable programs. Unlike the locally served version, a `file://` snapshot deliberately avoids storing filters in shareable URL query parameters. It does not install a service worker, update itself, collect usage statistics, or silently fetch new catalog entries.

For an optional regularly updated hosted site, see [GitHub Pages publishing](PAGES.md). This standalone snapshot builder **does not enable GitHub Pages or upload anything**.

## Tests and maintenance

Before submitting a PR, run:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
node --test tests/test_search.mjs tests/test_cli_csv_parity.mjs tests/test_offline_script.mjs tests/test_app_fallback.mjs
node --check site/app.mjs
python3 scripts/build_offline.py
```

The Node-based tests require **Node.js 22+** (installed automatically in GitHub Actions). Regular Python validation and the terminal explorer do *not* require Node.

The required content-validation workflow runs these checks on pull requests and `main`, including building and syntax-checking an offline export. Keep both interfaces in sync with changes to the catalog's identity and filter fields. The browser uses `textContent` and node creation instead of injecting resource strings into HTML, and validates official links before rendering them.

## Optional real-browser smoke checks

The core Atlas is still dependency-free. For **optional automated Chromium and Firefox QA**, install
Playwright in a separate Python environment and download each browser once:

```bash
python3 -m pip install playwright==1.57.0
python3 -m playwright install chromium firefox
python3 scripts/browser_smoke.py --browser chromium
python3 scripts/browser_smoke.py --browser firefox
```

On Windows, use `py -3 -m pip`, `py -3 -m playwright`, and
`py -3 scripts/browser_smoke.py --browser chromium` (or `--browser firefox`). The smoke script starts a loopback-only
server on a temporary port, exercises the locally served catalog, then shuts
the server down. It checks catalog rendering, search and filters, clear,
shareable URLs, keyboard shortcuts, visible skip-link focus, viewport
overflow, filtering after disconnecting the browser from the network, the
local no-JavaScript fallback, and browser-dependent `file://` behavior: either
successful local loading or an explanation that a server is required.
It reports the tested OS and browser version. It does not click external
upstream links or publish the site.

The [optional cross-browser workflow](../.github/workflows/browser-smoke.yml)
runs Chromium and Firefox independently when browser-facing files change in
pull requests and can also be started manually. These are **real browser
automation checks**, not a claim of a human accessibility audit. Manual
Firefox testing, screen-reader announcements, touch-device behavior,
visual inspection, and the complete manual checklist
still belong to [issue #10](https://github.com/sanskarIN/awesome-tech-atlas/issues/10).
The no-JavaScript fallback links to the **local** Markdown index so it can
work without internet access once repository files are available. Local
`file://` behavior differs between browsers; use a loopback HTTP server for
the most predictable experience.

## Hosting and releases

**A separate GitHub Pages publishing workflow is now available.** It packages the same static explorer and offline snapshot, but publishes only from the protected `main` branch after validation and only when the repository's Pages settings support GitHub Actions. Pull requests build without deployment privileges. See [the Pages runbook](PAGES.md) for setup, project base paths, verification, manual accessibility checks and rollback. The local explorer and the standalone snapshot builder do not publish anything on their own.

The offline export contains the original profiles stored in this repository, which are covered by its CC0 contribution policy. It does **not** bundle upstream manuals, third-party logos, images, or downloaded documentation.

No GitHub release tag is required for these continuously maintained content and tooling updates.
