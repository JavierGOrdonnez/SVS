#!/usr/bin/env python3
"""
Feminicide data extractor (T20) — CLI wrapper around feminicide_parser.py.

Target report: Delegación del Gobierno "Víctimas Mortales por Violencia de
Género" ficha (currently 2024 only; historical 2003-2023 counts live in
violence_spain.csv via T1's manual entries, not this file).

Parses each PDF via feminicide_parser.parse_pdf(), then writes two row types
to a single cumulative CSV: age-distribution rows and origin-distribution
rows (year, breakdown_type, category, victims_count, perpetrators_count,
confidence, notes).

Usage:
    python feminicide_extractor.py <pdf_dir> [output_csv]
"""

import sys
from pathlib import Path
from feminicide_parser import parse_pdf
from utils import write_csv_rows, cli_require_arg


def extract_to_csv(pdf_path: str, output_csv: str) -> None:
    """
    Parse one feminicide PDF and append its rows to `output_csv`.

    Writes two row types (columns: year, breakdown_type, category,
    victims_count, perpetrators_count, confidence, notes):
    1. breakdown_type='age': one row per age_group.
    2. breakdown_type='origin': one row per country-of-birth category.
    """
    result = parse_pdf(pdf_path)

    if 'error' in result:
        print(f"Error parsing {pdf_path}: {result['error']}")
        return

    year = result.get('year')
    if not year:
        print(f"Warning: Could not extract year from {pdf_path}")
        return

    rows = []

    # Extract age distribution
    if result.get('age'):
        for age in result['age']:
            rows.append({
                'year': year,
                'breakdown_type': 'age',
                'category': age['age_group'],
                'victims_count': age['victims_count'],
                'perpetrators_count': age['perpetrators_count'],
                'confidence': 'high',
                'notes': f'Age distribution from {Path(pdf_path).name}',
            })

    # Extract origin distribution
    if result.get('origin'):
        for origin in result['origin']:
            rows.append({
                'year': year,
                'breakdown_type': 'origin',
                'category': origin['origin'],
                'victims_count': origin['victims_count'],
                'perpetrators_count': origin['perpetrators_count'],
                'confidence': 'high',
                'notes': f'Origin distribution from {Path(pdf_path).name}',
            })

    # Write to CSV
    if rows:
        fieldnames = ['year', 'breakdown_type', 'category', 'victims_count',
                     'perpetrators_count', 'confidence', 'notes']
        write_csv_rows(output_csv, rows, fieldnames)
        print(f"Extracted {len(rows)} rows from {year}")


def batch_extract(pdf_dir: str, output_csv: str) -> None:
    """Process every PDF in `pdf_dir` and (re)generate `output_csv` from scratch."""
    pdf_path = Path(pdf_dir)
    if not pdf_path.exists():
        print(f"Error: Directory not found: {pdf_dir}")
        return

    # Clear output CSV
    Path(output_csv).unlink(missing_ok=True)

    pdfs = sorted(pdf_path.glob('*.pdf'))
    if not pdfs:
        print(f"No PDFs found in {pdf_dir}")
        return

    for pdf in pdfs:
        extract_to_csv(str(pdf), output_csv)

    print(f"\nCSV output: {output_csv}")


if __name__ == '__main__':
    cli_require_arg(sys.argv, [
        "Usage: feminicide_extractor.py <pdf_dir> [output_csv]",
        "  pdf_dir: Directory containing feminicide PDFs",
        "  output_csv: Output CSV file (default: data/raw/feminicidios_delegacion_2024.csv)",
    ])

    pdf_dir = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "data/raw/feminicidios_delegacion_2024.csv"

    batch_extract(pdf_dir, output_csv)
