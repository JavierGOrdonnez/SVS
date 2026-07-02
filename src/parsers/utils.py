#!/usr/bin/env python3
"""
Shared helpers for src/parsers/ scripts (T19-T21/T26/T27 PDF extractors).

Every parser here follows the same shape: shell out to `pdftotext` (or
pdfplumber, for mir_parser.py) to get raw text/tables, regex/parse it into
rows, then either print a summary (parser) or write CSV (extractor). This
module holds the 4 pieces that were previously copy-pasted with small,
accidental divergences across those files:

  extract_text     — pdftotext subprocess wrapper (layout mode, page range, timeout)
  write_csv_rows   — DictWriter with header-on-first-write, for append or overwrite
  parse_es_number  — Spanish-formatted number string ("1.234,5") -> float
  cli_require_arg  — argv length guard + usage message + exit(1)
"""

import csv
import re
import subprocess
import sys


def extract_text(pdf_path, layout=False, first_page=None, last_page=None, timeout=60):
    """Run pdftotext on `pdf_path` and return its stdout.

    layout: pass -layout (preserves column alignment; needed for regexes
        that match whitespace-separated columns).
    first_page/last_page: pass -f/-l to extract only a page range.
    Raises RuntimeError if pdftotext exits non-zero or times out.
    """
    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    if first_page is not None:
        cmd += ["-f", str(first_page)]
    if last_page is not None:
        cmd += ["-l", str(last_page)]
    cmd += [str(pdf_path), "-"]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {proc.stderr}")
    return proc.stdout


def write_csv_rows(path, rows, fieldnames, mode="a", quoting=csv.QUOTE_MINIMAL):
    """Write `rows` to `path` via csv.DictWriter, writing the header only if
    the file is currently empty (works for both append-across-many-calls use
    and single overwrite-with-full-row-list use, since a fresh 'w'-mode file
    always starts at position 0)."""
    with open(path, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=quoting)
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(rows)


_CLEAN_RE = re.compile(r"[^\d,.]")


def parse_es_number(s: str) -> float | None:
    """Parse Spanish-formatted number (dot=thousands, comma=decimal)."""
    if not s or s.strip() in ("", "-", "—", "N/A", "n/a"):
        return None
    s = _CLEAN_RE.sub("", s.strip())
    # Remove thousands dots if followed by exactly 3 digits (or end of string)
    s = re.sub(r"\.(?=\d{3}(?:[.,]|$))", "", s)
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def cli_require_arg(argv, usage_lines, min_len=2):
    """Exit(1) with `usage_lines` printed if argv has fewer than `min_len`
    entries. usage_lines may be a single string or a list of lines."""
    if len(argv) < min_len:
        lines = [usage_lines] if isinstance(usage_lines, str) else usage_lines
        for line in lines:
            print(line)
        sys.exit(1)
