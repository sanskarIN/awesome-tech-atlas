# Explore the atlas locally

Awesome Tech Atlas has two optional, **dependency-light** ways to browse the same curated `data/resources.json` file: a Python terminal explorer and a static HTML/CSS/JavaScript interface. Both are read-only. Neither edits the catalog, collects analytics, needs a database, or automatically deploys GitHub Pages.

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
python3 scripts/atlas.py show scikit-learn
```

On Windows, use `py -3` instead of `python3` if that is your configured launcher.

Search uses **AND** semantics for words, ignores case and most accents, and ranks title matches over summary matches. Category and kind filters use exact catalog identifiers (see `categories` and `kinds`). `--json` emits an array of complete catalog records for `search`, or the selected record for `show`. No results is not a command error; unknown resource IDs produce a nonzero exit status.

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

The interface provides visible labels, a keyboard skip link, dark-mode and reduced-motion support, and a live result count. Press **/** (outside form fields) to focus search; press **Escape** while typing in search to clear it. Filter state is stored only in the page URL query parameters so it can be shared. No cookies, local-storage history, third-party fonts, trackers, account login, or service worker are used.

**With JavaScript disabled or JSON loading blocked**, follow the Markdown catalog link on the page. The interactive interface is an enhancement, not the only way to discover resources.

The local search page loads only files from your own server. Clicking the **profile** opens GitHub and clicking the **official source** opens the upstream website, which require network access and have their own privacy and licensing policies. An inspection date is a documentation-review marker, **not** a runtime, performance, maintenance, or security guarantee.

## Tests and maintenance

Before submitting a PR, run:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
node --test tests/test_search.mjs
node --check site/app.mjs
```

The Node-based tests require **Node.js 22+** (installed automatically in GitHub Actions). Regular Python validation and the terminal explorer do *not* require Node.

The required content-validation workflow runs these checks on pull requests and `main`. Keep both interfaces in sync with changes to the catalog's identity and filter fields. The browser uses `textContent` and node creation instead of injecting resource strings into HTML, and validates official links before rendering them.

## Hosting and releases

**No GitHub Pages deployment is enabled by this feature.** The site is intentionally a local/static preview. Publishing it later would be a separate opt-in decision requiring a deployment configuration, a base-path check, and deployment verification. Do not approve unknown Pages deployments simply because this folder exists.

No GitHub release tag is required for these continuously maintained content and tooling updates.
