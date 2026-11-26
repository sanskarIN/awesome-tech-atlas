"""Regression coverage for the local terminal profile reader."""

import contextlib
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import atlas


class ProfileReaderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.profiles = self.root / "resources"
        self.profiles.mkdir()
        self.catalog = self.root / "catalog.json"
        self.records = [{
            "id": "sample",
            "name": "Sample",
            "category": "programming-languages",
            "subcategory": "Example",
            "kind": "official-docs",
            "summary": "Original description.",
            "url": "https://example.org/sample",
            "verified_on": "2026-11-26",
        }]
        self.catalog.write_text(json.dumps(self.records), encoding="utf-8")
        self.profile = self.profiles / "sample.md"
        self.markdown = "# Sample\r\n\r\nRésumé — नमस्ते\r\n\r\n<script>example</script>"
        self.profile.write_bytes(self.markdown.encode("utf-8"))

    def invoke(self, ident):
        output, error = StringIO(), StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            status = atlas.main([
                "--catalog", str(self.catalog), "profile", ident,
                "--root", str(self.root),
            ])
        return status, output.getvalue(), error.getvalue()

    def assert_failure(self, ident, message):
        status, output, error = self.invoke(ident)
        self.assertEqual(status, 1)
        self.assertEqual(output, "")
        self.assertIn(message, error)

    def test_returns_exact_original_markdown_without_rendering(self):
        before = self.profile.read_bytes()
        self.assertEqual(atlas.read_profile(self.records, "sample", self.root), self.markdown)
        self.assertEqual(self.invoke("sample"), (0, self.markdown, ""))
        self.assertEqual(self.profile.read_bytes(), before)

    def test_subprocess_preserves_utf8_bytes_and_line_endings(self):
        result = subprocess.run([
            sys.executable, str(atlas.ROOT / "scripts" / "atlas.py"),
            "--catalog", str(self.catalog), "profile", "sample",
            "--root", str(self.root),
        ], capture_output=True, check=True)
        self.assertEqual(result.stdout, self.profile.read_bytes())
        self.assertEqual(result.stderr, b"")

    def test_unknown_case_mismatch_and_traversal_are_rejected(self):
        for ident in ("missing", "Sample", "../sample", "sample.md", ""):
            with self.subTest(ident=ident):
                self.assert_failure(ident, "Unknown resource ID")

    def test_uncatalogued_file_cannot_be_read(self):
        (self.profiles / "unlisted.md").write_text("Unlisted", encoding="utf-8")
        self.assert_failure("unlisted", "Unknown resource ID")

    def test_missing_profile_fails_without_partial_output(self):
        self.profile.unlink()
        self.assert_failure("sample", "cannot read local UTF-8 profile")

    def test_invalid_utf8_fails_without_partial_output(self):
        self.profile.write_bytes(b"# Valid prefix\n\xff")
        self.assert_failure("sample", "cannot read local UTF-8 profile")

    def test_directory_is_not_a_profile(self):
        self.profile.unlink()
        self.profile.mkdir()
        self.assert_failure("sample", "not a regular file")

    def test_symlink_to_another_file_is_rejected(self):
        other = self.root / "outside.md"
        other.write_text("Outside the profile directory", encoding="utf-8")
        self.profile.unlink()
        try:
            self.profile.symlink_to(other)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"Symlink creation unavailable: {exc}")
        self.assert_failure("sample", "not a regular file")

    def test_real_catalog_profile_matches_source_file(self):
        records = atlas.load_catalog()
        ident = "scikit-learn"
        expected = (atlas.ROOT / "resources" / f"{ident}.md").read_bytes()
        self.assertEqual(atlas.read_profile(records, ident).encode("utf-8"), expected)


if __name__ == "__main__":
    unittest.main()
