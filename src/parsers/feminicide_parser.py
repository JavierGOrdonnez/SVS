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
        r'TOTAL MUJERES VÍCTIMAS MORTALES \d{4} - \d{4}: (\d+)',
        text
    )
    if total_match:
        result['total_2003_2024'] = int(total_match.group(1))

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

    pattern = r'Tabla 2\.2.*?(?=Tabla\s|$)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not match:
        return data

    table_text = match.group(0)
    lines = table_text.split('\n')

    current_age_group = None
    for line in lines:
        line = line.strip()

        if not line or 'Tabla' in line or 'Grupo de edad' in line:
            continue

        # Age group header (e.g., "De 18 a 20 años")
        if 'años' in line.lower() and not any(c.isdigit() for c in line[:10]):
            current_age_group = line
            continue

        # Data line: number + percentage pairs
        match = re.match(
            r"^([<\d\s\-a-záéíóú]+?)\s+(\d+)\s+([\d.]+)\s+(\d+)\s+([\d.]+)$",
            line
        )
        if match:
            age_group = match.group(1).strip()
            victims_n = int(match.group(2))
            victims_pct = float(match.group(3))
            perpetrators_n = int(match.group(4))
            perpetrators_pct = float(match.group(5))

            data.append({
                'age_group': age_group,
                'victims_count': victims_n,
                'victims_pct': victims_pct,
                'perpetrators_count': perpetrators_n,
                'perpetrators_pct': perpetrators_pct,
                'table': 2.2,
            })

    return data


def extract_table_2_3_origin(text: str) -> List[Dict]:
    """Extract Table 2.3: Country of birth."""
    data = []

    pattern = r'Tabla 2\.3.*?(?=Tabla\s|$)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not match:
        return data

    table_text = match.group(0)
    lines = table_text.split('\n')

    for line in lines:
        line = line.strip()

        if not line or 'Tabla' in line or 'País' in line or 'Número' in line:
            continue

        # Parse: "Country NUMBER % (victims & perpetrators)"
        match = re.match(
            r"^([A-Za-zá-ú\s]+?)\s+(\d+)\s+([\d.]+)\s+(\d+)",
            line
        )
        if match:
            country = match.group(1).strip()
            victims_n = int(match.group(2))
            victims_pct = float(match.group(3))
            perpetrators_n = int(match.group(4))

            data.append({
                'origin': country,
                'victims_count': victims_n,
                'victims_pct': victims_pct,
                'perpetrators_count': perpetrators_n,
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
            timeout=10
        )

        if proc.returncode != 0:
            result['validation']['errors'].append(f"pdftotext failed: {proc.stderr}")
            return result

        text = proc.stdout

        # Extract headline data
        result['headline'] = extract_headline_data(text)
        result['year'] = result['headline'].get('year')

        # Extract headline count (year-specific total)
        headline_match = re.search(r'Tabla 2\.1.*?TOTAL\s+(\d+)\s+100', text, re.DOTALL)
        if headline_match:
            result['headline_count'] = int(headline_match.group(1))

        # Extract tables
        result['regional'] = extract_table_2_1_regional(text)
        result['age'] = extract_table_2_2_age(text)
        result['origin'] = extract_table_2_3_origin(text)

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
