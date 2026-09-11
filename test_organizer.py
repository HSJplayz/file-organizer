#!/usr/bin/env python3
"""
Tests for the File Organizer.

Run with:  python -m unittest test_organizer -v
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import organizer


def _make(folder: Path, name: str, content: str = "x") -> Path:
    p = folder / name
    p.write_text(content, encoding="utf-8")
    return p


class TestCategorize(unittest.TestCase):
    def test_known_extensions(self):
        cases = {
            "a.jpg": "Images",
            "b.PNG": "Images",          # case-insensitive
            "c.pdf": "Documents",
            "d.mp3": "Audio",
            "e.mp4": "Video",
            "f.zip": "Archives",
            "g.py": "Code",
            "h.exe": "Installers",
        }
        for filename, expected in cases.items():
            self.assertEqual(organizer.categorize(Path(filename)), expected, filename)

    def test_unknown_extension_goes_to_others(self):
        self.assertEqual(organizer.categorize(Path("x.xyz123")), "Others")

    def test_no_extension_returns_none(self):
        self.assertIsNone(organizer.categorize(Path("README")))


class TestUniqueDest(unittest.TestCase):
    def test_free_name_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            self.assertEqual(organizer.unique_dest(d, "a.txt"), d / "a.txt")

    def test_conflict_gets_counter(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            _make(d, "a.txt")
            _make(d, "a_1.txt")
            self.assertEqual(organizer.unique_dest(d, "a.txt"), d / "a_2.txt")


class TestPlanAndExecute(unittest.TestCase):
    def test_plan_only_lists_files(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            _make(d, "one.jpg")
            _make(d, "two.txt")
            moves = organizer.plan(d)
            self.assertEqual(len(moves), 2)
            self.assertTrue(all(s.is_file() for s, _ in moves))

    def test_execute_moves_into_categories(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            _make(d, "one.jpg")
            _make(d, "two.txt")
            moves = organizer.plan(d)
            log = d / ".file_organizer_undo.json"
            organizer.execute(moves, log)
            self.assertTrue((d / "Images" / "one.jpg").exists())
            self.assertTrue((d / "Documents" / "two.txt").exists())
            self.assertTrue(log.exists())

    def test_undo_restores_files(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            _make(d, "one.jpg")
            moves = organizer.plan(d)
            log = d / ".file_organizer_undo.json"
            organizer.execute(moves, log)
            organizer.undo(d, log)
            self.assertTrue((d / "one.jpg").exists())
            self.assertFalse((d / "Images" / "one.jpg").exists())
            self.assertFalse(log.exists())

    def test_protected_folders_untouched(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "Code").mkdir()
            _make(d, "x.py")
            moves = organizer.plan(d)
            self.assertEqual(len(moves), 1)


if __name__ == "__main__":
    unittest.main()