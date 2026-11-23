"""GitHub Pages packaging regression checks (no network or external packages)."""

from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urljoin

from scripts import build_pages

ROOT = Path(__file__).resolve().parents[1]


class PagesBuilderTests(unittest.TestCase):
    def test_build_contains_live_assets_all_profiles_and_offline_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "published"
            output = build_pages.build_pages(target)
            records = json.loads((ROOT / "data/resources.json").read_text(encoding="utf-8"))
            page = (output / "site/index.html").read_text(encoding="utf-8")
            snapshot = (output / "downloads/awesome-tech-atlas-offline.html").read_text(encoding="utf-8")

            self.assertEqual(output, target)
            for filename in build_pages.SITE_FILES:
                self.assertTrue((output / "site" / filename).is_file())
            for name in ("index.html", "404.html", "robots.txt", "sitemap.xml", ".nojekyll"):
                self.assertTrue((output / name).is_file())
            self.assertTrue((output / build_pages.MARKER).is_file())
            self.assertEqual(
                json.loads((output / "data/resources.json").read_text(encoding="utf-8")),
                records,
            )
            self.assertEqual(
                {path.stem for path in (output / "resources").glob("*.md") if path.name != "README.md"},
                {record["id"] for record in records},
            )
            for record in records:
                name = record["id"] + ".md"
                self.assertEqual(
                    (output / "resources" / name).read_bytes(),
                    (ROOT / "resources" / name).read_bytes(),
                )
            self.assertIn('href="../downloads/awesome-tech-atlas-offline.html"', page)
            self.assertIn('href="../data/resources.json"', page)
            self.assertIn('href="../resources/README.md"', page)
            self.assertIn('href="./styles.css"', page)
            self.assertIn('src="./app.mjs"', page)
            self.assertIn('rel="canonical"', page)
            self.assertIn("globalThis.__ATLAS_EMBEDDED_CATALOG__", snapshot)
            self.assertIn("globalThis.__ATLAS_EMBEDDED_PROFILES__", snapshot)
            self.assertNotIn('src="./app.mjs"', snapshot)
            self.assertNotIn("Download offline HTML", (ROOT / "site/index.html").read_text())

    def test_project_base_path_resolves_all_relative_targets(self):
        base = "https://sanskarin.github.io/awesome-tech-atlas/"
        self.assertEqual(
            urljoin(base, "./site/"),
            base + "site/",
        )
        site_url = base + "site/"
        self.assertEqual(urljoin(site_url, "./app.mjs"), base + "site/app.mjs")
        self.assertEqual(urljoin(site_url, "./styles.css"), base + "site/styles.css")
        self.assertEqual(urljoin(site_url, "../data/resources.json"), base + "data/resources.json")
        self.assertEqual(urljoin(site_url, "../resources/README.md"), base + "resources/README.md")
        self.assertEqual(
            urljoin(site_url, "../downloads/awesome-tech-atlas-offline.html"),
            base + "downloads/awesome-tech-atlas-offline.html",
        )

    def test_repeated_build_cleans_only_marked_generated_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "pages"
            build_pages.build_pages(target)
            stale = target / "resources/stale.md"
            stale.write_text("outdated", encoding="utf-8")
            build_pages.build_pages(target)
            self.assertFalse(stale.exists())

            other = Path(directory) / "user-documents"
            other.mkdir()
            important = other / "keep.txt"
            important.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "refusing to delete"):
                build_pages.build_pages(other)
            self.assertEqual(important.read_text(), "keep")

    def test_invalid_destination_and_base_url_are_rejected(self):
        for address in (
            "http://example.com/atlas/",
            "https://example.com/atlas",
            "https://someone:pass@example.com/atlas/",
            "https://example.com/atlas/?q=x",
            "https://example.com/atlas/#fragment",
        ):
            with self.subTest(address=address):
                with self.assertRaises(ValueError):
                    build_pages.checked_base_url(address)
        for target in (ROOT, ROOT / "site", ROOT / "resources"):
            with self.subTest(path=target):
                with self.assertRaisesRegex(ValueError, "source files"):
                    build_pages.prepare_output(target, ROOT)

    def test_builder_fails_before_mutating_destination_on_profile_error(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "site"
            with patch.object(build_pages, "load_profiles", side_effect=ValueError("invalid profile")):
                with self.assertRaisesRegex(ValueError, "invalid profile"):
                    build_pages.build_pages(target)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
