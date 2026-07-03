#!/usr/bin/env python3
"""
MIR sexual violence data extractor (T32 input) — CLI wrapper around
mir_violence_parser.py.

Target report: Ministerio del Interior "Informe sobre la evolución de la
violencia contra la mujer", "Violencia Sexual" chapter (2015-2019 series).

Parses each PDF via mir_violence_parser.parse_pdf(), then writes all 5 tables
(crime-by-year, crime-by-age, crime-by-nationality, location-by-year,
relationship-by-year) to a single tidy CSV (columns: source_table, period,
year, crime_type, age_group, nationality, location, relationship, count,
confidence, notes).

Usage:
    python mir_violence_extractor.py <pdf_dir_or_file> [output_csv]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mir_violence_parser import parse_pdf
from utils import write_csv_rows, cli_require_arg


FIELDNAMES = ['source_table', 'period', 'year', 'crime_type', 'age_group',
              'nationality', 'location', 'relationship', 'count',
              'confidence', 'notes']


def extract_to_csv(pdf_path: str, output_csv: str) -> None:
    """Parse a MIR sexual-violence PDF and append its tables to a tidy CSV."""
    result = parse_pdf(pdf_path)

    if 'error' in result:
        print(f"Error parsing {pdf_path}: {result['error']}")
        return

    if not result['validation']['passed']:
        print(f"Warning: validation failed for {pdf_path}:")
        for err in result['validation']['errors']:
            print(f"  - {err}")

    period = result['period']
    notes = f"From {Path(pdf_path).name}, Violencia Sexual chapter"
    rows = []

    for row in result['crime_by_year']:
        rows.append({
            'source_table': 1, 'period': period, 'year': row['year'],
            'crime_type': row['crime_type'], 'count': row['count'],
            'confidence': 'high', 'notes': notes,
        })

    for row in result['crime_by_age']:
        rows.append({
            'source_table': 2, 'period': period, 'year': period,
            'crime_type': row['crime_type'], 'age_group': row['age_group'],
            'count': row['count'], 'confidence': 'high', 'notes': notes,
        })

    for row in result['crime_by_nationality']:
        rows.append({
            'source_table': 3, 'period': period, 'year': period,
            'crime_type': row['crime_type'], 'nationality': row['nationality'],
            'count': row['count'], 'confidence': 'high', 'notes': notes,
        })

    for row in result['location_by_year']:
        rows.append({
            'source_table': 4, 'period': period, 'year': row['year'],
            'location': row['location'], 'count': row['count'],
            'confidence': 'high', 'notes': notes,
        })

    for row in result['relationship_by_year']:
        rows.append({
            'source_table': 5, 'period': period, 'year': row['year'],
            'relationship': row['relationship'], 'count': row['count'],
            'confidence': 'high', 'notes': notes,
        })

    if rows:
        write_csv_rows(output_csv, rows, FIELDNAMES)
        print(f"Extracted {len(rows)} rows from {Path(pdf_path).name}")
    else:
        print(f"Skipped {Path(pdf_path).name}: no Violencia Sexual tables found "
              f"in pages 52-57 (unexpected layout)")


def batch_extract(pdf_dir: str, output_csv: str) -> None:
    """Process all PDFs in directory and generate cumulative CSV."""
    pdf_path = Path(pdf_dir)
    if not pdf_path.exists():
        print(f"Error: Directory not found: {pdf_dir}")
        return

    Path(output_csv).unlink(missing_ok=True)

    pdfs = sorted(pdf_path.glob('MIR_*.pdf'))
    if not pdfs:
        print(f"No MIR PDFs found in {pdf_dir}")
        return

    for pdf in pdfs:
        extract_to_csv(str(pdf), output_csv)

    print(f"\nCSV output: {output_csv}")


if __name__ == '__main__':
    cli_require_arg(sys.argv, [
        "Usage: mir_violence_extractor.py <pdf_dir_or_file> [output_csv]",
        "  pdf_dir_or_file: Directory containing MIR PDFs, or a single PDF",
        "  output_csv: Output CSV file (default: data/raw/mir_violence_sexual_2015-2019.csv)",
    ])

    pdf_arg = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "data/raw/mir_violence_sexual_2015-2019.csv"

    if Path(pdf_arg).is_dir():
        batch_extract(pdf_arg, output_csv)
    else:
        Path(output_csv).unlink(missing_ok=True)
        extract_to_csv(pdf_arg, output_csv)
        print(f"\nCSV output: {output_csv}")
