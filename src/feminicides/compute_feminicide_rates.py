#!/usr/bin/env python3
"""
Compute per-origin victim and perpetrator feminicide rates, 2006-2024.

Data sources:
- Feminicide victim/perpetrator counts (2006-2024) from Delegación del
  Gobierno (T19/T20 output), data/raw/feminicidios_delegacion_2003-2026.json
- Spanish/foreign-resident population by sex (2006-2024), read directly
  from INE t.56936, data/processed/population_spain_nationality.csv
  (T89/B44/V46) -- no subtraction across mismatched sources. Previously
  this file derived the Spanish figure as total population (INE Padrón)
  minus Eurostat migr_pop1ctz foreign stock, which mixed a July-1/January-1
  reference-date pair and a shifting ~86-94% foreign-coverage gap; see
  SPEC.md B44.
"""

import csv
import json
import sys

FEMINICIDE_JSON = 'data/raw/feminicidios_delegacion_2003-2026.json'
POPULATION_NATIONALITY_CSV = 'data/processed/population_spain_nationality.csv'
OUTPUT_CSV = 'data/processed/feminicide_rates_2006-2024.csv'

YEARS = range(2006, 2025)  # 2006-2024: T19's "modern-format" PDF coverage,
                           # capped by population_spain_midyear_5yr.csv (through 2024)

ORIGIN_LABELS = {'españa': 'España', 'otro_pais': 'Otro país'}
ROLES = ('victim', 'perpetrator')


def load_feminicide_data():
    """Load feminicide victim and perpetrator counts by origin for each year
    in YEARS."""
    with open(FEMINICIDE_JSON, encoding='utf-8') as f:
        dataset = json.load(f)

    data = {}
    for report in dataset['reports']:
        year = report['year']
        if year not in YEARS:
            continue
        data[year] = {
            entry['label']: {
                'victim': entry['victim_count'],
                'perpetrator': entry['perp_count'],
            }
            for entry in report['origin']
        }
    return data


def load_population_by_nationality():
    """{(year, sex, nationality): population}, sex in female/male,
    nationality in spanish/foreign/total, age_group=all, read directly from
    INE t.56936 (T89/B44/V46) -- no subtraction."""
    result = {}
    with open(POPULATION_NATIONALITY_CSV, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['age_group'] != 'all' or row['sex'] not in ('female', 'male'):
                continue
            year = int(row['year'])
            if year not in YEARS:
                continue
            result[(year, row['sex'], row['nationality'])] = int(row['population_july1'])
    return result


def estimate_nationality_population(year, pop_by_key, sex):
    """
    Population (for a given sex) by origin (Spanish resident vs foreign
    resident) for `year`, read directly from INE t.56936 (T89/B44/V46) --
    no derivation, both figures are source-reported.
    """
    spanish = pop_by_key[(year, sex, 'spanish')]
    foreign = pop_by_key[(year, sex, 'foreign')]
    total = pop_by_key.get((year, sex, 'total'), spanish + foreign)

    return {
        'españa': spanish,
        'otro_pais': foreign,
        'total': total,
    }


def compute_rates():
    """Compute feminicide victim and perpetrator rates per 100k population,
    for every year in YEARS that has both a feminicide report
    and population data."""
    fem_data = load_feminicide_data()
    pop_by_key = load_population_by_nationality()

    sex_by_role = {'victim': 'female', 'perpetrator': 'male'}

    results = []
    for year in YEARS:
        if year not in fem_data:
            continue

        for role in ROLES:
            sex = sex_by_role[role]
            if (year, sex, 'spanish') not in pop_by_key or (year, sex, 'foreign') not in pop_by_key:
                continue
            pop_data = estimate_nationality_population(year, pop_by_key, sex)

            for origin in ['españa', 'otro_pais']:
                count = fem_data[year].get(ORIGIN_LABELS[origin], {}).get(role, 0)
                pop = pop_data[origin]

                # Rate per 100,000
                rate_per_100k = (count / pop) * 100_000 if pop > 0 else 0

                sex_label = 'female' if role == 'victim' else 'male'
                results.append({
                    'year': year,
                    'origin': origin,
                    'role': role,
                    'count': count,
                    'population': int(pop),
                    'rate_per_100k': round(rate_per_100k, 2),
                    'confidence': 'medium',
                    'notes': (
                        f'{origin} {year} {role} — counts: Delegación del Gobierno '
                        f'(high confidence); population: INE t.56936, direct '
                        f'Spanish/foreign {sex_label} nationality split (T89/B44/V46), '
                        f'not derived by subtraction'
                    ),
                })

    return results


def write_output(results):
    """Write results to CSV."""
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['year', 'origin', 'role', 'count', 'population', 'rate_per_100k',
                     'confidence', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Rates written to {OUTPUT_CSV}")

    # Print summary for the latest year only
    latest_year = max(r['year'] for r in results)
    for r in results:
        if r['year'] != latest_year:
            continue
        print(f"\n{r['year']} {r['origin'].upper()} ({r['role']})")
        print(f"  Count: {r['count']}")
        print(f"  Population: {r['population']:,}")
        print(f"  Rate: {r['rate_per_100k']}/100k")


if __name__ == '__main__':
    rates = compute_rates()
    write_output(rates)
