#!/usr/bin/env python3
"""
File Organizer
==============
A safe CLI tool that sorts a messy folder (e.g. your Downloads) into organized
subfolders by file type. Includes a --dry-run preview mode and an --undo option
so nothing is ever destroyed by accident.

Used as Day 1 of the daily projects streak.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Category configuration: extension -> category folder name
# --------------------------------------------------------------------------- #
CATEGORIES: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".heic", ".raw"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx", ".epub"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".rb", ".php", ".sh", ".sql", ".ipynb", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".appimage"],
}

# Files we should never try to move (special/system names).
PROTECTED = {".", "..", "Images", "Documents", "Audio", "Video", "Archives", "Code", "Installers", "Others"}


def categorize(path: Path) -> str | None:
    """Return the target category folder name for a file, or None if unknown."""
    ext = path.suffix.lower()
    for category, exts in CATEGORIES.items():
        if ext in exts:
            return category
    if ext:
        return "Others"
    return None  # no extension at all -> skip


def list_files(folder: Path) -> list[Path]:
    """Return top-level files (not subdirs) in the folder."""
    return [p for p in folder.iterdir() if p.is_file()]


def unique_dest(base: Path, filename: str) -> Path:
    """Return a destination path that won't clobber an existing file."""
    candidate = base / filename
    if not candidate.exists():
        return candidate
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = base / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def plan(folder: Path) -> list[tuple[Path, Path]]:
    """Compute the list of (source, destination) moves without executing them."""
    moves: list[tuple[Path, Path]] = []
    for src in list_files(folder):
        category = categorize(src)
        if category is None:
            continue
        dest_dir = folder / category
        dest = unique_dest(dest_dir, src.name)
        moves.append((src, dest))
    return moves


def execute(moves: list[tuple[Path, Path]], log_path: Path) -> None:
    """Perform the moves and record them in a JSON undo-log."""
    log: list[dict] = []
    for src, dest in moves:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        log.append({"from": str(src), "to": str(dest)})
        print(f"  {src.name}  ->  {dest.parent.name}/{dest.name}")
    with log_path.open("w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)
    print(f"\nUndo-log written to: {log_path}")


def undo(folder: Path, log_path: Path) -> None:
    """Revert a previous run using its JSON undo-log."""
    if not log_path.exists():
        print(f"No undo log found at {log_path}")
        return
    with log_path.open("r", encoding="utf-8") as fh:
        log = json.load(fh)
    # Reverse so we undo in last-in-first-out order.
    for entry in reversed(log):
        dest = Path(entry["to"])
        src = Path(entry["from"])
        if dest.exists():
            src.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest), str(src))
            print(f"  {dest.name}  ->  {src}")
    # Remove the now-consumed log.
    log_path.unlink(missing_ok=True)
    print("\nUndo complete.")


def summary(moves: list[tuple[Path, Path]]) -> None:
    if not moves:
        print("Nothing to organize — folder is already tidy.")
        return
    counts: dict[str, int] = {}
    for _, dest in moves:
        counts[dest.parent.name] = counts.get(dest.parent.name, 0) + 1
    print("\nSummary:")
    for category, count in sorted(counts.items()):
        print(f"  {category:12s} {count} file(s)")
    print(f"\nTotal: {len(moves)} file(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Sort a messy folder into subfolders by file type.",
    )
    parser.add_argument("folder", nargs="?", default=".",
                        help="Path to the folder to organize (default: current dir)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview the moves without changing anything (default: ON for safety use --run)")
    parser.add_argument("--run", action="store_true",
                        help="Actually perform the moves (required to make changes)")
    parser.add_argument("--undo", action="store_true",
                        help="Revert the previous run using its undo-log")
    args = parser.parse_args(argv)

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: not a directory -> {folder}", file=sys.stderr)
        return 1

    log_path = folder / ".file_organizer_undo.json"

    if args.undo:
        undo(folder, log_path)
        return 0

    moves = plan(folder)
    summary(moves)

    if args.run:
        print("\nExecuting moves...")
        execute(moves, log_path)
    else:
        print("\n--- DRY RUN (no changes made) ---")
        print("Re-run with --run to apply, or --undo to revert a previous run.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
