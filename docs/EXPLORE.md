# Explore the atlas locally

Awesome Tech Atlas has three optional, **dependency-light** ways to browse the same curated `data/resources.json` file: a Python terminal explorer, a locally served static browser, and a generated single-file offline snapshot. All three are read-only: none edits the catalog, collects analytics, needs a database, or automatically deploys GitHub Pages.

The original [Markdown resource index](../resources/README.md) remains the primary, durable source. Every resource still needs a human-reviewed profile and an upstream reference.

## Option A: Search from a terminal

Requires **Python 3.10+** and only the standard library. From the repository root:

```bash
python3 scripts/atlas.py stats
python3 scripts/atlas.py categories
python3 scripts/atlas.py kinds
python3 scripts/atlas.py search rust
python3 scripts/atlas.py search "machine learning" --limit 8
python3 scripts/atlas.py search database --category databases-storage --json
python3 scripts/atlas.py search rust --csv > rust-resources.csv
python3 scripts/atlas.py search "machine learning" --limit 8 --csv > ml-resources.csv
python3 scripts/atlas.py show scikit-learn
```

On Windows, use `py -3` instead of `python3` if that is your configured launcher.

Search uses **AND** semantics for words, ignores case and most accents, and ranks title matches over summary matches. Category and kind filters use exact catalog identifiers (see `categories` and `kinds`). `--json` emits an array of complete catalog records for `search`, or the selected record for `show`. For `search`, `--csv` emits the **same columns and match order as the browser's CSV exporter**, with quoted UTF-8 cells, CRLF rows, and a leading apostrophe on formula-like values to prevent spreadsheet evaluation. Use either `--json` or `--csv`, not both. `--csv` prints a header even when there are zero matches, so pipelines can handle empty results consistently. The CLI writes raw UTF-8 without a byte-order mark; the browser adds a UTF-8 BOM to its downloaded CSV for spreadsheet compatibility. Treat formula safety as a defensive export measure, not a substitute for reviewing untrusted source data. No results is not a command error; unknown resource IDs produce a nonzero exit status.

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

The interface provides visible labels, a keyboard skip link, dark-mode and reduced-motion support, and a live result count. **Download matching results CSV** saves only the current search/filter matches, in display order, with titles, topics, official URLs, and inspection dates; it makes no network request. CSV fields are quoted, and formula-like values are prefixed to prevent spreadsheet interpretation. Press **/** (outside form fields) to focus search; press **Escape** while typing in search to clear it. Filter state is stored only in the page URL query parameters so it can be shared. No cookies, local-storage history, third-party fonts, trackers, account login, or service worker are used.

**When JavaScript is disabled**, use the Markdown catalog link on the page. **When catalog loading fails**, the explorer reveals a direct link to the local Markdown resource index, which can also be opened from disk. The interactive interface is an enhancement, not the only way to discover resources.

The local search page loads only files from your own server. Clicking the **profile** opens GitHub and clicking the **official source** opens the upstream website, which require network access and have their own privacy and licensing policies. An inspection date is a documentation-review marker, **not** a runtime, performance, maintenance, or security guarantee.

## Option C: Build a fully offline searchable HTML file

No JavaScript package installation, database, or hosted web server is required. With Python 3.10+ available, run from the **repository root**:

```bash
python3 scripts/build_offline.py
```

On Windows, use `py -3 scripts/build_offline.py`. The command generates:

```text
dist/awesome-tech-atlas-offline.html
```

Double-click that file to open it with a modern browser. The HTML includes the catalog JSON, **all 30 original curated resource profiles**, local search/filter code, and styles in **one file**. Search, category filters, kind filters, a **Download snapshot JSON** button, and **Download matching results CSV** work even with your network disconnected.

- Select a resource title to open its complete profile in an offline dialog. The profile is deliberately displayed as **plain Markdown text**, preserving examples, links, headings, and code exactly rather than attempting an incomplete or unsafe Markdown renderer.
- Use **Download Markdown** in the dialog to save the original profile locally. Press **Escape** or **Close** to return to the search results.
- The **View on GitHub** and **Official source** links still open external websites if network access is available.
- With JavaScript disabled, the generated HTML contains an offline expandable resource index with each complete profile as escaped plain text, not just a summary.

The exporter fails if a catalog profile is missing or its official URL disagrees with the catalog. Catalog data and Markdown profiles are embedded without creating new editorial content or updating source inspection dates.

The result is a snapshot of the catalog at build time. **Rebuild it after changing resource data.** Files under `dist/` are ignored by Git and should not be committed automatically. To choose a destination:

```bash
python3 scripts/build_offline.py --output my-offline-atlas.html
```

**Offline limits:** The embedded curated profiles can be read, searched by catalog metadata, and saved without internet. Links to GitHub, official upstream manuals, and other external pages still need connectivity. Profile text is shown as Markdown source rather than formatted HTML; snippets are documentation, not executable programs. Unlike the locally served version, a `file://` snapshot deliberately avoids storing filters in shareable URL query parameters. It does not install a service worker, update itself, collect usage statistics, or silently fetch new catalog entries.

For a shareable or regularly updated hosted site, a separate deployment decision and testing process would be required. This builder **does not enable GitHub Pages or upload anything**.

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

## Hosting and releases

**No GitHub Pages deployment is enabled by this feature.** The hosted site remains a local/static preview, while the optional single-file HTML build is an offline snapshot. Publishing it later would be a separate opt-in decision requiring a deployment configuration, a base-path check, and deployment verification. Do not approve unknown Pages deployments simply because this folder exists.

The offline export contains the original profiles stored in this repository, which are covered by its CC0 contribution policy. It does **not** bundle upstream manuals, third-party logos, images, or downloaded documentation.

No GitHub release tag is required for these continuously maintained content and tooling updates.
