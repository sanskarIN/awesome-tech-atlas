#!/usr/bin/env python3
"""Build a vetted, path-safe GitHub Pages artifact without third-party dependencies.

The local explorer and the single-file offline snapshot remain independent.
This command only writes local files; deployment is handled by GitHub Actions.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import shutil
from urllib.parse import urlsplit

if __package__:
    from .build_offline import build_offline_html, load_profiles, replace_exactly_once, verify_records
else:
    from build_offline import build_offline_html, load_profiles, replace_exactly_once, verify_records

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "pages"
DEFAULT_BASE_URL = "https://sanskarin.github.io/awesome-tech-atlas/"
MARKER = ".atlas-pages-build"
SITE_FILES = ("index.html", "app.mjs", "search.mjs", "styles.css")
DOWNLOAD_NAME = "awesome-tech-atlas-offline.html"


def checked_base_url(value: str) -> str:
    """Require an HTTPS directory URL; never silently lose the project path."""
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not parsed.path.endswith("/")
        or "//" in parsed.path
    ):
        raise ValueError("Pages base URL must be an HTTPS directory URL ending in '/'.")
    return value


def prepare_output(output: Path, root: Path) -> None:
    """Rebuild only marked generated folders, never arbitrary source directories."""
    output = output.resolve()
    root = root.resolve()
    if root.is_relative_to(output) or (output.is_relative_to(root) and not output.is_relative_to(root / "dist")):
        raise ValueError("Output must not overwrite repository source files.")
    if output.exists():
        if not output.is_dir():
            raise ValueError("Output path exists but is not a directory.")
        if any(output.iterdir()):
            if not (output / MARKER).is_file():
                raise ValueError("Nonempty output folder is not an Atlas Pages build; refusing to delete.")
            shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)


def build_pages(
    output: Path = DEFAULT_OUTPUT,
    *,
    root: Path = ROOT,
    base_url: str = DEFAULT_BASE_URL,
) -> Path:
    """Copy only known assets and every catalog-matched profile into a static site."""
    base_url = checked_base_url(base_url)
    root = Path(root).resolve()
    output = Path(output).resolve()

    records = verify_records(json.loads((root / "data/resources.json").read_text(encoding="utf-8")))
    # Catch missing or mismatched curated profiles BEFORE deleting an existing build.
    load_profiles(root, records)
    snapshot = build_offline_html(root=root, records=records)

    prepare_output(output, root)
    for part in ("site", "data", "resources", "downloads"):
        (output / part).mkdir()

    for filename in SITE_FILES:
        shutil.copy2(root / "site" / filename, output / "site" / filename)
    shutil.copy2(root / "data/resources.json", output / "data/resources.json")
    shutil.copy2(root / "resources/README.md", output / "resources/README.md")
    for record in records:
        filename = record["id"] + ".md"
        shutil.copy2(root / "resources" / filename, output / "resources" / filename)

    page_path = output / "site/index.html"
    page = page_path.read_text(encoding="utf-8")
    page = replace_exactly_once(
        page,
        '<a href="../data/resources.json" class="data-link" download>Get catalog JSON</a>',
        '<a href="../data/resources.json" class="data-link" download>Get catalog JSON</a>\n'
        '          <a href="../downloads/awesome-tech-atlas-offline.html" '
        'class="data-link" download>Download offline HTML</a>',
    )
    page = replace_exactly_once(
        page,
        "<title>Explore resources | Awesome Tech Atlas</title>",
        "<title>Explore resources | Awesome Tech Atlas</title>\n"
        f'  <link rel="canonical" href="{html.escape(base_url + "site/", quote=True)}">',
    )
    page_path.write_text(page, encoding="utf-8")

    (output / "downloads" / DOWNLOAD_NAME).write_text(snapshot, encoding="utf-8")
    (output / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n'
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '  <meta name="robots" content="noindex,follow">\n'
        '  <meta http-equiv="refresh" content="0; url=./site/">\n'
        '  <title>Awesome Tech Atlas</title>\n'
        '</head>\n<body>\n'
        '  <main><h1>Awesome Tech Atlas</h1>\n'
        '  <p><a href="./site/">Open the resource explorer</a>.</p></main>\n'
        '</body>\n</html>\n',
        encoding="utf-8",
    )
    (output / "404.html").write_text(
        '<!doctype html>\n<html lang="en">\n<head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Page not found | Awesome Tech Atlas</title></head>\n'
        '<body><main><h1>Page not found</h1><p>That address is not part of the atlas. '
        f'<a href="{html.escape(base_url + "site/", quote=True)}">'
        'Return to the resource explorer</a>.</p></main></body>\n</html>\n',
        encoding="utf-8",
    )
    (output / "robots.txt").write_text(
        f"Sitemap: {base_url}sitemap.xml\n", encoding="utf-8"
    )
    (output / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{html.escape(base_url + "site/")}</loc></url>\n'
        '</urlset>\n',
        encoding="utf-8",
    )
    (output / ".nojekyll").touch()
    (output / MARKER).write_text("Generated by scripts/build_pages.py\n", encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args(argv)
    target = build_pages(args.output, base_url=args.base_url)
    print(f"Built Atlas Pages artifact at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
