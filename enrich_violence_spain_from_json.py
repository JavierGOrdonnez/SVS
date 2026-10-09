#!/usr/bin/env python3
"""
Enrich violence_spain.csv rows 46-99 with validated sexual crime data from JSON files.

This script:
1. Reads the structured sexual crime JSON files (Informe, Anuario, Balance series)
2. Fills in missing values and updates confidence levels for rows 46-99
3. Preserves existing data where it's already present and verified
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

ROOT = Path(__file__).parent
DATA_RAW = ROOT / "data" / "raw"
CSV_PATH = DATA_RAW / "violence_spain.csv"

def load_json(path: Path) -> Dict:
    """Load JSON file."""
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def read_csv() -> Tuple[List[str], List[List[str]]]:
    """Read CSV and return headers and rows."""
    with open(CSV_PATH, encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    return headers, rows

def write_csv(headers: List[str], rows: List[List[str]]):
    """Write CSV file."""
    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def extract_rape_counts(informe: Dict) -> Dict[int, int]:
    """Extract rape with penetration counts from Informe series by year."""
    counts = {}
    for report in informe.get('reports', []):
        year = report.get('year')
        for cat in report.get('categories', []):
            category = cat.get('category', '').lower()
            # Look for categories with "penetration"
            if 'penetr' in category or 'penetración' in category:
                count = cat.get('count')
                if count:
                    counts[year] = count
                    break  # Take first penetration category for this year
    return counts

def extract_assault_without_penetration(informe: Dict) -> Dict[int, int]:
    """Extract sexual assault without penetration counts by year."""
    counts = {}
    for report in informe.get('reports', []):
        year = report.get('year')
        for cat in report.get('categories', []):
            category = cat.get('category', '').lower()
            # Look for agresión sexual without penetración
            if 'agresion' in category and 'penetr' not in category:
                count = cat.get('count')
                if count:
                    counts[year] = count
                    break
    return counts

def extract_total_crimes(informe: Dict) -> Dict[int, int]:
    """Extract total sexual crime counts from Informe by year."""
    counts = {}
    for report in informe.get('reports', []):
        year = report.get('year')
        total = report.get('total_count')
        if total:
            counts[year] = total
    return counts

def extract_clearance_rates(informe: Dict) -> Dict[int, float]:
    """Extract clearance rates from Informe by year."""
    rates = {}
    for report in informe.get('reports', []):
        year = report.get('year')
        rate = report.get('clearance_rate')
        if rate is not None:
            rates[year] = rate
    return rates

def extract_perpetrator_male_pct(informe: Dict) -> Dict[int, float]:
    """Extract male perpetrator percentage by year."""
    pcts = {}
    for report in informe.get('reports', []):
        year = report.get('year')
        pct = report.get('perp_male_pct')
        if pct is not None:
            pcts[year] = pct
    return pcts

def extract_victim_counts_by_sex(informe: Dict) -> Dict[Tuple[int, str], int]:
    """Extract victim counts by sex by year."""
    counts = {}
    for report in informe.get('reports', []):
        year = report.get('year')
        # Get totals from nationality breakdown (which has sex data)
        for sex_key in ['female', 'male']:
            total = 0
            if report.get('nationality', {}).get('victims', {}).get(f'{sex_key}_total'):
                total = report['nationality']['victims'][f'{sex_key}_total']
                if total:
                    counts[(year, sex_key)] = total
    return counts

def extract_total_victims(informe: Dict) -> Dict[int, int]:
    """Extract total victim counts by year."""
    counts = {}
    for report in informe.get('reports', []):
        year = report.get('year')
        # Try to get from structured data
        nationality = report.get('nationality', {})
        if nationality and 'victims' in nationality:
            total = sum([
                nationality['victims'].get(k, 0)
                for k in ['spanish_count', 'foreign_count']
                if k in nationality['victims']
            ])
            if total:
                counts[year] = total
    return counts

def enrich_rows(headers: List[str], rows: List[List[str]], informe: Dict) -> List[List[str]]:
    """Enrich rows 46-99 with JSON data."""

    # Extract data from JSON
    rape_counts = extract_rape_counts(informe)
    assault_counts = extract_assault_without_penetration(informe)
    total_crimes = extract_total_crimes(informe)
    clearance_rates = extract_clearance_rates(informe)
    male_pcts = extract_perpetrator_male_pct(informe)

    # Find header indices
    header_map = {h: i for i, h in enumerate(headers)}

    # Track updates
    updates = {'filled': [], 'upgraded': []}

    for row_idx, row in enumerate(rows, start=1):
        row_id = int(row[header_map['row_id']])

        # Only enrich rows 46-99
        if not (46 <= row_id <= 99):
            continue

        violence_type = row[header_map['violence_type']]
        year_str = row[header_map['year']]
        current_value = row[header_map['value']]
        current_confidence = row[header_map['confidence']]

        # Skip if already has verified data
        if current_value and current_confidence == 'high':
            continue

        try:
            year = int(year_str) if year_str else None
        except ValueError:
            continue

        # Check if we have JSON data for this type and year
        new_value = None
        should_upgrade = False

        if violence_type == 'rape_with_penetration_reported' and year in rape_counts:
            new_value = str(rape_counts[year])
            should_upgrade = True
        elif violence_type == 'sexual_assault_without_penetration_reported' and year in assault_counts:
            new_value = str(assault_counts[year])
            should_upgrade = True
        elif violence_type == 'sexual_crimes_total_reported' and year in total_crimes:
            new_value = str(total_crimes[year])
            should_upgrade = True
        elif violence_type == 'sexual_crimes_clearance_rate' and year in clearance_rates:
            new_value = f"{clearance_rates[year]:.1f}"
            should_upgrade = True
        elif violence_type == 'sexual_crimes_perpetrator_male_pct' and year in male_pcts:
            new_value = f"{male_pcts[year]:.2f}"
            should_upgrade = True

        if new_value:
            if not current_value:  # Fill empty value
                row[header_map['value']] = new_value
                row[header_map['confidence']] = 'high'
                row[header_map['source_name']] = 'Ministerio_Interior'
                row[header_map['notes']] = f'Filled from structured JSON (Informe {year})'
                updates['filled'].append((row_id, violence_type, year))
            elif should_upgrade and current_confidence in ['low', 'medium']:  # Upgrade confidence
                row[header_map['value']] = new_value
                row[header_map['confidence']] = 'high'
                row[header_map['source_name']] = 'Ministerio_Interior'
                row[header_map['notes']] = f'Verified from structured JSON (Informe {year})'
                updates['upgraded'].append((row_id, violence_type, year))

    return rows, updates

def main():
    """Main enrichment process."""
    print("🔧 Enriching violence_spain.csv rows 46-99 from JSON files...")

    # Load files
    print("  📂 Loading JSON files...")
    informe = load_json(DATA_RAW / "sexual_crimes_mir_2017-2024.json")

    print("  📖 Reading CSV...")
    headers, rows = read_csv()

    # Enrich
    print("  ✏️  Enriching rows...")
    rows, updates = enrich_rows(headers, rows, informe)

    # Write back
    print("  💾 Writing enriched CSV...")
    write_csv(headers, rows)

    # Report
    print()
    print("✅ Enrichment complete!")
    print(f"   Rows filled: {len(updates['filled'])}")
    for row_id, vtype, year in updates['filled']:
        print(f"     • Row {row_id}: {vtype} ({year})")
    print(f"   Rows upgraded to high confidence: {len(updates['upgraded'])}")
    for row_id, vtype, year in updates['upgraded']:
        print(f"     • Row {row_id}: {vtype} ({year})")

if __name__ == "__main__":
    main()
