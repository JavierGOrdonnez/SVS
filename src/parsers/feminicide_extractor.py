#!/usr/bin/env python3
"""
Feminicide data extractor — parse PDFs and generate CSV output.
Converts parser output (age/origin demographics) to structured CSV.
"""

import sys
import csv
import json
from pathlib import Path
from feminicide_parser import parse_pdf


def extract_to_csv(pdf_path: str, output_csv: str) -> None:
    """
    Parse feminicide PDF and output structured CSV.

    Two sets of rows:
    1. Age distribution: (year, age_group, total victims, total perpetrators)
    2. Origin distribution: (year, origin, total victims, total perpetrators)
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
        with open(output_csv, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            # Only write header if file is new
            if f.tell() == 0:
                writer.writeheader()
            writer.writerows(rows)
        print(f"✓ Extracted {len(rows)} rows from {year}")


def batch_extract(pdf_dir: str, output_csv: str) -> None:
    """Process all PDFs in directory and generate cumulative CSV."""
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

    print(f"\n✓ CSV output: {output_csv}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: feminicide_extractor.py <pdf_dir> [output_csv]")
        print("  pdf_dir: Directory containing feminicide PDFs")
        print("  output_csv: Output CSV file (default: data/raw/feminicidios_delegacion_2003-2026.csv)")
        sys.exit(1)

    pdf_dir = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "data/raw/feminicidios_delegacion_2003-2026.csv"

    batch_extract(pdf_dir, output_csv)
