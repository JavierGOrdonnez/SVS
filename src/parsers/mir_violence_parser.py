#!/usr/bin/env python3
"""
MIR Sexual Violence PDF Parser with Integrated Validation

Extracts data from Ministerio del Interior "Informe sobre la evolución de la
violencia contra la mujer" PDFs, "Violencia Sexual" chapter (2015-2019 series).

Tables extracted:
  - Table 1: Victimizations by crime type and year
  - Table 2: Victimizations by crime type and victim age group
  - Table 3: Victimizations by crime type and victim nationality
  - Table 4: Victimizations by location of offense and year
  - Table 5: Victimizations by victim-offender relationship and year

Input: a single source PDF (pages 52-57 by default; MIR_ViolenceWomen_2015-2019.pdf).
Output: parse_pdf() returns a dict of 5 row-lists (stdout summary only — see
mir_violence_extractor.py for the CSV-writing CLI).
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from utils import extract_text, parse_es_number, cli_require_arg


CRIME_TYPES = ['ABUSO SEXUAL', 'AGRESIÓN SEXUAL', 'AGRESIÓN SEXUAL CON PENETRACIÓN',
               'ABUSO SEXUAL CON PENETRACIÓN', 'ACOSO SEXUAL', 'MUTILACION GENITAL']

# Table 3 lists crime types in a different order than Tables 1 and 2.
CRIME_TYPES_NATIONALITY = ['ABUSO SEXUAL', 'ABUSO SEXUAL CON PENETRACIÓN', 'ACOSO SEXUAL',
                            'AGRESIÓN SEXUAL', 'AGRESIÓN SEXUAL CON PENETRACIÓN', 'MUTILACION GENITAL']

YEARS = ['2015', '2016', '2017', '2018', '2019', '2015-2019']
AGE_GROUPS = ['Descon.', 'Menor', '18-30', '31-40', '41-50', '51-65', '>65', 'TOTAL']
NATIONALITIES = ['Española', 'Extranjera', 'TOTAL']
LOCATIONS = ['VIVIENDAS Y ANEXOS', 'VÍAS DE COMUNICACIÓN', 'INSTALACIONES Y RECINTOS',
             'ESTABLECIMIENTOS', 'ESPACIOS ABIERTOS', 'MEDIOS DE TRANSPORTE']
RELATIONSHIPS = ['Violencia de género', 'Violencia doméstica', 'Violencia otras relaciones']

# Six whitespace-separated numbers (one per year, plus the 2015-2019 total).
NUM6 = r'([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)'


def to_num(s: str) -> int:
    """Convert a Spanish-formatted integer string ('23.706') to int."""
    return int(parse_es_number(s))


def extract_table_1_crime_by_year(raw: str) -> List[Dict]:
    """Table 1: Victimizations by crime type and year (2015-2019)."""
    data = []

    m = re.search(
        r'Distribución de las victimizaciones por tipología delictiva.*?MUTILACION GENITAL\s*\n(.*?)Total VICTIMIZACIONES\s*\n'
        r'\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)',
        raw, re.DOTALL
    )
    if not m:
        return data

    nums = [to_num(x) for x in re.findall(r'[\d.]+', m.group(1))]
    totals = [to_num(g) for g in m.groups()[1:]]
    if len(nums) != len(CRIME_TYPES) * len(YEARS):
        return data

    for ci, year in enumerate(YEARS):
        col = nums[ci * 6:(ci + 1) * 6]
        for crime, val in zip(CRIME_TYPES, col):
            data.append({'crime_type': crime, 'year': year, 'count': val, 'table': 1})
        data.append({'crime_type': 'TOTAL', 'year': year, 'count': totals[ci], 'table': 1})

    return data


def extract_table_2_crime_by_age(raw: str) -> List[Dict]:
    """Table 2: Victimizations by crime type and victim age group (2015-2019)."""
    data = []

    chunk_m = re.search(
        r'>> Victimizaciones registradas según tipología delictiva y grupo de edad.*?(?=>> Edad de la víctima)',
        raw, re.DOTALL
    )
    if not chunk_m:
        return data

    nums = [to_num(x) for x in re.findall(r'^\s*([\d.]+)\s*$', chunk_m.group(0), re.MULTILINE)]
    if len(nums) != (len(CRIME_TYPES) + 1) * len(AGE_GROUPS):
        return data

    crime_block_size = len(CRIME_TYPES) * len(AGE_GROUPS)
    crime_block = nums[:crime_block_size]
    totals = nums[crime_block_size:]
    for ci, age in enumerate(AGE_GROUPS):
        col = crime_block[ci * 6:(ci + 1) * 6]
        for crime, val in zip(CRIME_TYPES, col):
            data.append({'crime_type': crime, 'age_group': age, 'count': val, 'table': 2})
        data.append({'crime_type': 'TOTAL', 'age_group': age, 'count': totals[ci], 'table': 2})

    return data


def extract_table_3_crime_by_nationality(raw: str) -> List[Dict]:
    """Table 3: Victimizations by crime type and victim nationality (2015-2019)."""
    data = []

    m = re.search(
        r'TIPO DE HECHO\n(?:[^\n]+\n){6}\nEspañ\.\n\n(.*?)\nTOTAL\n\n([\d.]+)\n\n([\d.]+)\n\n([\d.]+)',
        raw, re.DOTALL
    )
    if not m:
        return data

    nums = [to_num(x) for x in re.findall(r'[\d.]+', m.group(1))]
    totals = [to_num(g) for g in m.groups()[1:]]
    if len(nums) != len(CRIME_TYPES_NATIONALITY) * len(NATIONALITIES):
        return data

    for ci, nat in enumerate(NATIONALITIES):
        col = nums[ci * 6:(ci + 1) * 6]
        for crime, val in zip(CRIME_TYPES_NATIONALITY, col):
            data.append({'crime_type': crime, 'nationality': nat, 'count': val, 'table': 3})
        data.append({'crime_type': 'TOTAL', 'nationality': nat, 'count': totals[ci], 'table': 3})

    return data


def extract_table_4_location_by_year(layout: str) -> List[Dict]:
    """Table 4: Victimizations by location of offense and year (2015-2019)."""
    data = []

    sec_m = re.search(
        r'>> Distribución de victimizaciones por lugar de comisión.*?(?=>> |\Z)',
        layout, re.DOTALL
    )
    if not sec_m:
        return data
    sec = sec_m.group(0)

    for loc in LOCATIONS:
        rm = re.search(r'^\s*' + re.escape(loc) + r'\s+' + NUM6 + r'\s+[\d,]+\s*$', sec, re.MULTILINE)
        if not rm:
            return []
        for year, val in zip(YEARS, [to_num(x) for x in rm.groups()]):
            data.append({'location': loc, 'year': year, 'count': val, 'table': 4})

    tot_m = re.search(r'^\s*TOTAL\s+' + NUM6 + r'\s*$', sec, re.MULTILINE)
    if not tot_m:
        return []
    for year, val in zip(YEARS, [to_num(x) for x in tot_m.groups()]):
        data.append({'location': 'TOTAL', 'year': year, 'count': val, 'table': 4})

    return data


def extract_table_5_relationship_by_year(layout: str) -> List[Dict]:
    """Table 5: Victimizations by victim-offender relationship and year (2015-2019)."""
    data = []

    patterns = {
        'Violencia de género': r'Violencia de género: cónyuge, pareja, expareja,\s*\n\s*' + NUM6,
        'Violencia doméstica': r'Violencia doméstica: madre, hija y resto de\s*\n\s*' + NUM6,
        'Violencia otras relaciones': r'Violencia otras relaciones: conocido/vecindad,\s*' + NUM6,
    }

    for rel, pattern in patterns.items():
        m = re.search(pattern, layout)
        if not m:
            return []
        for year, val in zip(YEARS, [to_num(x) for x in m.groups()]):
            data.append({'relationship': rel, 'year': year, 'count': val, 'table': 5})

    tot_m = re.search(r'TOTAL VIOLENCIA SEXUAL\s+' + NUM6, layout)
    if not tot_m:
        return []
    for year, val in zip(YEARS, [to_num(x) for x in tot_m.groups()]):
        data.append({'relationship': 'TOTAL', 'year': year, 'count': val, 'table': 5})

    return data


def validate_extraction(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validation gates:
    - Within each table, the category rows for a given column (year / age
      group / nationality) must sum to that column's TOTAL row.
    - The 2015-2019 grand total from Table 1 must match the TOTAL/TOTAL
      cells of Tables 2-5.
    - Per-year TOTAL values must agree across Tables 1, 4 and 5.
    """
    errors = []

    def lookup(rows, key_field, key_val, group_field, group_val):
        for row in rows:
            if row[key_field] == key_val and row[group_field] == group_val:
                return row['count']
        return None

    def check_columns(rows, key_field, group_field, groups, table_name):
        for group in groups:
            total = lookup(rows, key_field, 'TOTAL', group_field, group)
            s = sum(r['count'] for r in rows if r[key_field] != 'TOTAL' and r[group_field] == group)
            if total is not None and s != total:
                errors.append(f"{table_name} ({group}): sum {s} != TOTAL {total}")

    t1 = data.get('crime_by_year', [])
    t2 = data.get('crime_by_age', [])
    t3 = data.get('crime_by_nationality', [])
    t4 = data.get('location_by_year', [])
    t5 = data.get('relationship_by_year', [])

    check_columns(t1, 'crime_type', 'year', YEARS, 'Table 1')
    check_columns(t2, 'crime_type', 'age_group', AGE_GROUPS, 'Table 2')
    check_columns(t3, 'crime_type', 'nationality', NATIONALITIES, 'Table 3')
    check_columns(t4, 'location', 'year', YEARS, 'Table 4')
    check_columns(t5, 'relationship', 'year', YEARS, 'Table 5')

    grand_total = lookup(t1, 'crime_type', 'TOTAL', 'year', '2015-2019')
    if grand_total is not None:
        cross_totals = {
            'Table 2': lookup(t2, 'crime_type', 'TOTAL', 'age_group', 'TOTAL'),
            'Table 3': lookup(t3, 'crime_type', 'TOTAL', 'nationality', 'TOTAL'),
            'Table 4': lookup(t4, 'location', 'TOTAL', 'year', '2015-2019'),
            'Table 5': lookup(t5, 'relationship', 'TOTAL', 'year', '2015-2019'),
        }
        for name, val in cross_totals.items():
            if val is not None and val != grand_total:
                errors.append(f"{name} grand total {val} != Table 1 grand total {grand_total}")

        for year in YEARS:
            v1 = lookup(t1, 'crime_type', 'TOTAL', 'year', year)
            v4 = lookup(t4, 'location', 'TOTAL', 'year', year)
            v5 = lookup(t5, 'relationship', 'TOTAL', 'year', year)
            vals = {v for v in (v1, v4, v5) if v is not None}
            if len(vals) > 1:
                errors.append(f"TOTAL mismatch for {year}: Table1={v1}, Table4={v4}, Table5={v5}")

    return len(errors) == 0, errors


def parse_pdf(pdf_path: str, first_page: int = 52, last_page: int = 57) -> Dict:
    """
    Parse the "Violencia Sexual" chapter of a MIR violence-against-women PDF.

    Returns:
    {
        'file': str,
        'period': '2015-2019',
        'crime_by_year': [dict],
        'crime_by_age': [dict],
        'crime_by_nationality': [dict],
        'location_by_year': [dict],
        'relationship_by_year': [dict],
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
        'period': '2015-2019',
        'crime_by_year': [],
        'crime_by_age': [],
        'crime_by_nationality': [],
        'location_by_year': [],
        'relationship_by_year': [],
        'validation': {'passed': True, 'errors': []},
    }

    try:
        raw = extract_text(pdf_path, first_page=first_page, last_page=last_page, timeout=60)
        layout = extract_text(pdf_path, layout=True, first_page=first_page, last_page=last_page, timeout=60)

        result['crime_by_year'] = extract_table_1_crime_by_year(raw)
        result['crime_by_age'] = extract_table_2_crime_by_age(raw)
        result['crime_by_nationality'] = extract_table_3_crime_by_nationality(raw)
        result['location_by_year'] = extract_table_4_location_by_year(layout)
        result['relationship_by_year'] = extract_table_5_relationship_by_year(layout)

        is_valid, errors = validate_extraction(result)
        result['validation']['passed'] = is_valid
        result['validation']['errors'] = errors

    except subprocess.TimeoutExpired:
        result['validation']['passed'] = False
        result['validation']['errors'].append("PDF extraction timeout")
    except Exception as e:
        result['validation']['passed'] = False
        result['validation']['errors'].append(f"PDF parsing error: {e}")

    return result


def main():
    """Command-line interface."""
    cli_require_arg(sys.argv, "Usage: mir_violence_parser.py <pdf_path> [first_page] [last_page]")

    pdf_path = sys.argv[1]
    first_page = int(sys.argv[2]) if len(sys.argv) > 2 else 52
    last_page = int(sys.argv[3]) if len(sys.argv) > 3 else 57

    result = parse_pdf(pdf_path, first_page, last_page)

    if 'error' in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    print("=== MIR SEXUAL VIOLENCE PDF PARSER ===")
    print(f"File: {result['file']}")
    print(f"Period: {result['period']}")

    print("\nTables extracted:")
    print(f"  - Crime by year: {len(result['crime_by_year'])} rows")
    print(f"  - Crime by age group: {len(result['crime_by_age'])} rows")
    print(f"  - Crime by nationality: {len(result['crime_by_nationality'])} rows")
    print(f"  - Location by year: {len(result['location_by_year'])} rows")
    print(f"  - Relationship by year: {len(result['relationship_by_year'])} rows")

    print(f"\nValidation: {'PASS' if result['validation']['passed'] else 'FAIL'}")
    if result['validation']['errors']:
        print("Errors:")
        for err in result['validation']['errors']:
            print(f"  - {err}")

    grand_total = next(
        (r['count'] for r in result['crime_by_year']
         if r['crime_type'] == 'TOTAL' and r['year'] == '2015-2019'), None
    )
    print(f"\nTotal victimizations 2015-2019: {grand_total}")

    print("\nSample crime-by-year data (2015-2019 totals):")
    for row in result['crime_by_year']:
        if row['year'] == '2015-2019':
            print(f"  {row['crime_type']}: {row['count']}")


if __name__ == '__main__':
    main()
