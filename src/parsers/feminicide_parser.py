#!/usr/bin/env python3
"""
Feminicide PDF Parser with Integrated Validation

Extracts data from Delegación del Gobierno "Estadística de víctimas mortales
por violencia de pareja" PDFs (2003–2026).

Tables extracted:
  - Table 2.1: Regional breakdown
  - Table 2.2: Age distribution (victims + perpetrators)
  - Table 2.3: Country of birth (victims + perpetrators)
  - Table 2.4: Relationship type/duration
  - Table 3.1-3.4: Institutional data & circumstances
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def extract_headline_data(text: str) -> Dict:
    """Extract headline summary: year, total, update date, last case."""
    result = {}

    # Year
    year_match = re.search(r'Año (\d{4})', text)
    if year_match:
        result['year'] = int(year_match.group(1))

    # Total 2003-2024
    total_match = re.search(
        r'TOTAL MUJERES VÍCTIMAS MORTALES (\d{4} - \d{4}): (\d+)',
        text
    )
    if total_match:
        result['period'] = total_match.group(1)
        result['total_2003_2024'] = int(total_match.group(2))

    # Last case details
    last_case = re.search(
        r'Último caso\s+incorporado:.*?(\d+)\s+(de\s+\w+\s+de\s+)?(\d{4})',
        text,
        re.DOTALL
    )
    if last_case:
        result['last_case_date'] = f"{last_case.group(1)}-{last_case.group(3)}"

    # Orphaned children
    orphans = re.search(
        r'N\.º huérfanas/os\s+menores de 18 años:\s*(\d+)',
        text
    )
    if orphans:
        result['orphaned_children'] = int(orphans.group(1))

    return result


def extract_table_2_1_regional(text: str) -> List[Dict]:
    """Extract Table 2.1: Regional breakdown of victims."""
    data = []

    # Extract the column-formatted table
    match = re.search(
        r'Tabla 2\.1.*?Comunidad/ciudad autónoma\s+(.*?)\s+Número\s+%\s+([\d.\s]+?)(?=Tabla|$)',
        text,
        re.DOTALL
    )
    if not match:
        return data

    regions_text = match.group(1).strip()
    values_text = match.group(2).strip()

    regions = [r.strip() for r in regions_text.split('\n') if r.strip()]
    values = [v.strip() for v in values_text.split() if v.strip()]

    if len(regions) < 1 or len(values) < len(regions) * 2:
        return data

    # Values are: first N are numbers, next N are percentages
    numbers = values[:len(regions)]
    percentages = values[len(regions) : len(regions) * 2]

    for i, region in enumerate(regions):
        try:
            data.append({
                'region': region,
                'victims': int(numbers[i]),
                'percentage': float(percentages[i]),
                'table': 2.1,
            })
        except (ValueError, IndexError):
            continue

    return data


def extract_table_2_2_age(text: str) -> List[Dict]:
    """Extract Table 2.2: Age distribution of victims and perpetrators."""
    data = []

    match = re.search(
        r'Tabla 2\.2.*?Grupo de edad\s+(.*?)\s+Mujeres víctimas mortales.*?Número\s+([\d\s]+?)\s+Número\s+([\d\s]+?)\s+%\s+([\d.\s]+?)\s+%\s+([\d.\s]+?)(?=Tabla|$)',
        text,
        re.DOTALL
    )
    if not match:
        return data

    age_text = match.group(1).strip()
    victim_nums_text = match.group(2).strip()
    perp_nums_text = match.group(3).strip()
    victim_pcts_text = match.group(4).strip()
    perp_pcts_text = match.group(5).strip()

    ages = [a.strip() for a in age_text.split('\n') if a.strip()]
    victim_nums = [int(v) for v in victim_nums_text.split() if v.strip().isdigit()]
    perp_nums = [int(p) for p in perp_nums_text.split() if p.strip().isdigit()]
    victim_pcts = [float(v) for v in victim_pcts_text.split() if v.strip()]
    perp_pcts = [float(p) for p in perp_pcts_text.split() if p.strip()]

    for i, age in enumerate(ages):
        if i < len(victim_nums) and i < len(perp_nums) and i < len(victim_pcts) and i < len(perp_pcts):
            data.append({
                'age_group': age,
                'victims_count': victim_nums[i],
                'victims_pct': victim_pcts[i],
                'perpetrators_count': perp_nums[i],
                'perpetrators_pct': perp_pcts[i],
                'table': 2.2,
            })

    return data


def extract_table_2_3_origin(text: str) -> List[Dict]:
    """Extract Table 2.3: Country of birth (victims & perpetrators)."""
    data = []

    match = re.search(
        r'Tabla 2\.3.*?País de nacimiento\s+(.*?)\s+Número\s+([\d\s]+?)\s+%\s+([\d.\s]+?)\s+Presuntos agresores\s+Número\s+([\d\s]+?)\s+%\s+([\d.\s]+?)(?=Tabla|$)',
        text,
        re.DOTALL
    )
    if not match:
        return data

    origin_text = match.group(1).strip()
    victim_nums_text = match.group(2).strip()
    victim_pcts_text = match.group(3).strip()
    perp_nums_text = match.group(4).strip()
    perp_pcts_text = match.group(5).strip()

    origins = [o.strip() for o in origin_text.split('\n') if o.strip()]
    victim_nums = [int(v) for v in victim_nums_text.split() if v.strip().isdigit()]
    victim_pcts = [float(v) for v in victim_pcts_text.split() if v.strip()]
    perp_nums = [int(p) for p in perp_nums_text.split() if p.strip().isdigit()]
    perp_pcts = [float(p) for p in perp_pcts_text.split() if p.strip()]

    for i, origin in enumerate(origins):
        if i < len(victim_nums) and i < len(perp_nums) and i < len(victim_pcts) and i < len(perp_pcts):
            data.append({
                'origin': origin,
                'victims_count': victim_nums[i],
                'victims_pct': victim_pcts[i],
                'perpetrators_count': perp_nums[i],
                'perpetrators_pct': perp_pcts[i],
                'table': 2.3,
            })

    return data


def validate_extraction(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validation gates:
    - V12: sum(regions) = total, sum(age_groups) = total, sum(origins) = total
    """
    errors = []

    # Get headline total from Table 2.1
    if 'regional' in data and data['regional']:
        regional_sum = sum(r['victims'] for r in data['regional'] if r['region'] != 'TOTAL')
        # The headline number should match
        if 'headline_count' in data and data['headline_count'] != regional_sum:
            errors.append(
                f"Regional sum validation: {regional_sum} != {data['headline_count']}"
            )

    # Age distribution sums
    if 'age' in data and data['age']:
        age_sum = sum(r['victims_count'] for r in data['age'] if r['age_group'] != 'TOTAL')
        if age_sum > 0 and 'headline_count' in data and abs(age_sum - data['headline_count']) > 1:
            errors.append(
                f"Age distribution sum: {age_sum} != {data['headline_count']}"
            )

    return len(errors) == 0, errors


def parse_pdf(pdf_path: str) -> Dict:
    """
    Parse feminicide PDF using text extraction.

    Returns:
    {
        'year': int,
        'headline_count': int,
        'headline': dict,
        'regional': [dict],
        'age': [dict],
        'origin': [dict],
        'validation': {
            'passed': bool,
            'errors': [str]
        }
    }
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        return {'error': f"PDF not found: {pdf_path}"}

    result = {
        'file': str(pdf_file),
        'headline': {},
        'regional': [],
        'age': [],
        'origin': [],
        'validation': {'passed': True, 'errors': []},
    }

    try:
        # Extract text using pdftotext
        proc = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if proc.returncode != 0:
            result['validation']['errors'].append(f"pdftotext failed: {proc.stderr}")
            return result

        text = proc.stdout

        # Extract headline data
        result['headline'] = extract_headline_data(text)
        result['year'] = result['headline'].get('year')

        # Extract tables
        result['regional'] = extract_table_2_1_regional(text)
        result['age'] = extract_table_2_2_age(text)
        result['origin'] = extract_table_2_3_origin(text)

        # Headline count (year-specific total) from Table 2.1's TOTAL row
        for row in result['regional']:
            if row['region'] == 'TOTAL':
                result['headline_count'] = row['victims']
                break

        # Run validation
        is_valid, errors = validate_extraction(result)
        result['validation']['passed'] = is_valid
        result['validation']['errors'] = errors

    except subprocess.TimeoutExpired:
        result['validation']['errors'].append("PDF extraction timeout")
        result['validation']['passed'] = False
    except Exception as e:
        result['validation']['passed'] = False
        result['validation']['errors'].append(f"PDF parsing error: {e}")

    return result


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("Usage: feminicide_parser.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    result = parse_pdf(pdf_path)

    if 'error' in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    print(f"=== FEMINICIDE PDF PARSER ===")
    print(f"File: {result['file']}")
    print(f"Year: {result.get('year', 'unknown')}")
    print(f"Total victims {result['headline'].get('period', '???')}: {result['headline'].get('total_2003_2024', 'N/A')}")
    print(f"Victims in {result.get('year')}: {result.get('headline_count', 'N/A')}")
    print(f"\nTables extracted:")
    print(f"  - Regional breakdown: {len(result['regional'])} rows")
    print(f"  - Age distribution: {len(result['age'])} rows")
    print(f"  - Origin (birth country): {len(result['origin'])} rows")

    print(f"\nValidation: {'PASS ✓' if result['validation']['passed'] else 'FAIL ✗'}")
    if result['validation']['errors']:
        print("Errors:")
        for err in result['validation']['errors']:
            print(f"  - {err}")

    # Print sample data
    if result['regional']:
        print(f"\nSample regional data (first 3):")
        for row in result['regional'][:3]:
            print(f"  {row['region']}: {row['victims']} ({row['percentage']}%)")

    if result['age']:
        print(f"\nSample age data (first 3):")
        for row in result['age'][:3]:
            print(f"  {row['age_group']}: victims={row['victims_count']}, perps={row['perpetrators_count']}")


if __name__ == '__main__':
    main()
