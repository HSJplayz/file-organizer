# 📁 File Organizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![CI](https://github.com/HSJplayz/file-organizer/actions/workflows/ci.yml/badge.svg)](https://github.com/HSJplayz/file-organizer/actions)
[![Streak Day 1](https://img.shields.io/badge/Streak-Day%201-green.svg)](https://github.com/HSJplayz/streak)

> A safe, zero-dependency CLI tool that turns a messy Downloads-style folder into tidy, extension-based subfolders — with a **dry-run preview**, an **undo log**, and **auto deduplication**.

## Table of Contents
- [Description](#description)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Project Structure](#project-structure)
- [Future Scope](#future-scope)
- [License](#license)

## Description
Your Downloads folder is chaos — PDFs, images, installers, code files and random.zip's all piled together. **File Organizer** scans a folder, groups files into category folders (`Images`, `Documents`, `Audio`, `Video`, `Archives`, `Code`, `Installers`, `Others`), and moves them — **safely**.

It's built around two guardrails so it never hurts your data:
- **`--dry-run`** (default) previews every move before anything happens.
- **`--undo`** reverts the last run using an auto-generated JSON log.

Built as **Day 1** of the [daily projects streak](https://github.com/HSJplayz/streak).

## Tech Stack
- **Python 3.10+** (standard library only — no third-party dependencies)
- `pathlib`, `shutil`, `argparse`, `json`

## Features
- Sort by file type into category subfolders.
- **Dry-run preview** — safe by default, nothing moves until you say `--run`.
- **Undo** — every run writes `.file_organizer_undo.json`; revert with `--undo`.
- **Auto-deduplication** — name conflicts become `file_1.pdf`, `file_2.pdf` instead of overwrites.
- **Protection** — never touches special/system entries or the category folders themselves.
- Clear per-category summary of what was organized.
- Fully configurable category rules (edit `CATEGORIES` in `organizer.py`).

## Installation
No install needed — Python 3.10+ is the only requirement.
```bash
git clone https://github.com/HSJplayz/file-organizer.git
cd file-organizer
```

## Usage
```bash
# 1. Preview what would happen (default, safe)
python organizer.py "C:\Users\you\Downloads"

# 2. Actually organize the folder
python organizer.py "C:\Users\you\Downloads" --run

# 3. Undo the last run
python organizer.py "C:\Users\you\Downloads" --undo
```

## Example
Before:
```
Downloads/
  photo1.png   report.pdf   setup.exe   song.mp3   code.py   data.csv   notes.docx
```
After `--run`:
```
Downloads/
  Images/    photo1.png
  Documents/ report.pdf  data.csv  notes.docx
  Installers/ setup.exe
  Audio/     song.mp3
  Code/      code.py
  .file_organizer_undo.json
```

## Project Structure
```
file-organizer/
  organizer.py        ← full CLI tool
  README.md
  LICENSE             ← MIT
  .gitignore
```

## Future Scope
- **Watchdog mode** — auto-organize new files as they land (background daemon).
- **Custom rules file** — user-defined patterns (regex) beyond plain extensions.
- **GUI / tray app** — one-click organizer for non-technical users.
- **Cloud sync handlers** — Google Drive / S3 source or destination.
- **Recursive mode** — flatten nested subfolders up into categories.
- **Dry-run report export** — write the plan to a CSV/Markdown file.

## License
[MIT](LICENSE)
