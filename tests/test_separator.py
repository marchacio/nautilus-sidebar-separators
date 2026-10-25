#!/usr/bin/env python3
"""
Unit tests for nautilus-separator CLI and bookmarks parsing logic.
"""

from importlib.machinery import SourceFileLoader
from pathlib import Path
import tempfile
import unittest

CLI_PATH = Path(__file__).resolve().parent.parent / "bin" / "nautilus-separator"
cli = SourceFileLoader("nautilus_separator", str(CLI_PATH)).load_module()


class TestNautilusSeparatorCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Patch module paths to use temporary directory
        self.orig_bookmarks_file = cli.BOOKMARKS_FILE
        self.orig_base_dir = cli.SEPARATORS_BASE_DIR

        cli.BOOKMARKS_FILE = self.temp_path / "bookmarks"
        cli.SEPARATORS_BASE_DIR = self.temp_path / "separators"

    def tearDown(self):
        cli.BOOKMARKS_FILE = self.orig_bookmarks_file
        cli.SEPARATORS_BASE_DIR = self.orig_base_dir
        self.temp_dir.cleanup()

    def test_slugify(self):
        self.assertEqual(cli.slugify("Work Projects"), "work-projects")
        self.assertEqual(cli.slugify("UNIVERSITÀ"), "universita")
        self.assertEqual(cli.slugify("C++ & Rust Code!"), "c-rust-code")
        self.assertEqual(cli.slugify("   leading and trailing  "), "leading-and-trailing")

    def test_add_separator(self):
        res = cli.add_separator("PROJECTS", no_restart=True)
        self.assertEqual(res, 0)

        # Verify bookmark was written
        lines = cli.read_bookmarks()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].endswith("# PROJECTS"))
        self.assertIn("file://", lines[0])

        # Verify dummy directory exists with marker
        slug_dir = cli.SEPARATORS_BASE_DIR / "projects"
        self.assertTrue(slug_dir.is_dir())
        self.assertTrue((slug_dir / ".nautilus-separator").is_file())

    def test_add_separator_duplicate_slug_updates_label(self):
        cli.add_separator("OLD NAME", custom_slug="custom-section", no_restart=True)
        cli.add_separator("NEW NAME", custom_slug="custom-section", no_restart=True)

        lines = cli.read_bookmarks()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].endswith("# NEW NAME"))

    def test_remove_separator_by_name_and_slug(self):
        cli.add_separator("CATEGORY ONE", no_restart=True)
        cli.add_separator("CATEGORY TWO", no_restart=True)
        self.assertEqual(len(cli.read_bookmarks()), 2)

        # Remove by name
        res = cli.remove_separator("CATEGORY ONE", no_restart=True)
        self.assertEqual(res, 0)
        lines = cli.read_bookmarks()
        self.assertEqual(len(lines), 1)
        self.assertTrue(lines[0].endswith("# CATEGORY TWO"))
        self.assertFalse((cli.SEPARATORS_BASE_DIR / "category-one").exists())

        # Remove by slug
        res = cli.remove_separator("category-two", no_restart=True)
        self.assertEqual(res, 0)
        self.assertEqual(len(cli.read_bookmarks()), 0)
        self.assertFalse((cli.SEPARATORS_BASE_DIR / "category-two").exists())

    def test_clean_all(self):
        cli.add_separator("SEC 1", no_restart=True)
        cli.add_separator("SEC 2", no_restart=True)
        self.assertEqual(len(cli.read_bookmarks()), 2)

        res = cli.clean_all(no_restart=True)
        self.assertEqual(res, 0)
        self.assertEqual(len(cli.read_bookmarks()), 0)
        self.assertEqual(len(list(cli.SEPARATORS_BASE_DIR.glob("*"))), 0)


if __name__ == "__main__":
    unittest.main()
