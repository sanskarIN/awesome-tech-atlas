# GitHub Pages publication runbook

Awesome Tech Atlas uses a **static, local-first** browser with a canonical
JSON catalog and reviewed Markdown profiles. Publishing is optional; the
repository and its offline snapshot remain usable without a hosted website.

## Publication address and repository setting

Expected public address after a successful deployment:

- Homepage: https://sanskarin.github.io/awesome-tech-atlas/
- Explorer: https://sanskarin.github.io/awesome-tech-atlas/site/
- Curated catalog: https://sanskarin.github.io/awesome-tech-atlas/data/resources.json
- Standalone offline HTML: https://sanskarin.github.io/awesome-tech-atlas/downloads/awesome-tech-atlas-offline.html

The homepage redirects to the explorer. Its separate site subdirectory is
deliberate: JavaScript and fallback links use relative paths such as
../data/resources.json and ../resources/README.md. Publishing only the site/
folder at the project root would **break** these links.

**One-time setting:** A repository administrator must choose
**Settings → Pages → Build and deployment → Source → GitHub Actions**.
The workflow cannot be assumed to enable or change that setting on its own.
The repository must permit GitHub Actions and Pages; an environment protection
rule, if configured, may require a manual deployment approval.

## What gets deployed

The workflow at .github/workflows/pages.yml does the following:

1. Run the existing content/link validator and Python/Node regression tests.
2. Execute python3 scripts/build_pages.py (stdlib-only).
3. Package exactly the browser assets, curated JSON, Markdown profile index,
   catalog-linked profiles, and a generated **single-file offline snapshot**.
4. Upload that directory as the Pages artifact.
5. Deploy **only** after successful checks on main, with narrowly scoped
   pages:write and id-token:write permissions. Pull requests perform a
   build-only check and cannot deploy.

Generated files are placed in dist/pages/ by default and are Git-ignored.
There is no tracking, third-party font, remote API, or service worker. The
original curated content is CC0-dedicated; externally linked resources retain
their own terms. The artifact does not download or mirror upstream manuals.

No API keys or personal data are needed for building or browsing.

## Local rehearsal

From the repository root:

    python3 scripts/validate.py
    python3 -m unittest discover -s tests -v
    node --check site/app.mjs
    node --test tests/test_search.mjs tests/test_cli_csv_parity.mjs tests/test_offline_script.mjs tests/test_app_fallback.mjs
    python3 scripts/build_pages.py

The local Pages artifact lives in dist/pages/. To preview the exact layout:

    cd dist/pages
    python3 -m http.server 8000 --bind 127.0.0.1

Visit http://127.0.0.1:8000/ or http://127.0.0.1:8000/site/.
The plain local explorer at repo-root/site/ still works as before.

To test under a project prefix, serve from the parent of a directory called
awesome-tech-atlas containing the build output. A correct deployment must
resolve /awesome-tech-atlas/site/ and /awesome-tech-atlas/data/resources.json
under the *same* prefix, not at the domain root.

## Activation and post-deploy verification

1. Review and merge the Pages publishing PR once validation and browser smoke
   checks pass. No release or git tag is needed.
2. Select GitHub Actions under the repository's Pages settings, if not already
   selected. Inspect the workflow run named "Build and publish Awesome Tech Atlas".
3. Verify the deploy job reports success and the GitHub Pages environment shows
   the public URL.
4. In a browser, open the homepage and confirm it lands on the explorer.
   Search, filter, clear filters, and compare 2–3 entries. Refresh a copied
   filtered URL and verify the same selection is restored.
5. Open a profile and an official upstream source. Download JSON, CSV and
   offline HTML; disconnect from the network and open the offline file to
   confirm its embedded catalog and profiles still work.
6. Check keyboard navigation, the skip link, dark mode, mobile layouts and
   at least one screen reader manually. Issue #10 tracks this outstanding
   accessibility/real-browser review; automated smoke tests do not close it.
7. Confirm /awesome-tech-atlas/robots.txt and sitemap.xml resolve and that
   the deployed site uses no analytics or unexpected network requests.

**Do not claim the public site is live merely because the repository has
has_pages=true or because an artifact was uploaded.** Confirm the deploy job
and test the public URL.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Site returns 404 | Pages Source must be GitHub Actions; verify a successful deploy from main and the repository's Pages environment URL. |
| Browser loads but catalog fails | Check that /awesome-tech-atlas/data/resources.json returns JSON and that site/ and data/ were deployed as siblings. |
| "Get catalog JSON" works locally but fails online | Do not upload only site/ or rewrite the application base URI to the domain root. Rebuild with scripts/build_pages.py. |
| PR build passes but no site appears | This is expected: PRs intentionally do not deploy. Merge after review, then check the main push workflow. |
| A deploy job is awaiting approval | Inspect environment protection rules and approve only after reviewing the exact workflow and source commit. |
| Artifact build refuses to delete a directory | The builder only cleans its own marked generated output; choose an empty destination or remove an obsolete directory yourself. |

## Rollback

Disable publishing in Settings → Pages or revert the publishing workflow
through an ordinary reviewed PR. Previously generated Pages content may
remain visible until GitHub completes the publishing change. To undo only
a site-content regression, revert the offending main commit and verify a new
deployment run.

The manual verification checklist remains in
[issue #10](https://github.com/sanskarIN/awesome-tech-atlas/issues/10).
