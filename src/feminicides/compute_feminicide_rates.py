#!/usr/bin/env python3
"""
Compute per-origin victim and perpetrator feminicide rates, 2006-2024.

Data sources:
- Feminicide victim/perpetrator counts (2006-2024) from Delegación del
  Gobierno (T19/T20 output), data/raw/feminicidios_delegacion_2003-2026.json
- Total female population (victim-rate denominator, 2006-2024) and total
  male population (perpetrator-rate denominator, 2006-2024) from INE Padrón
  midyear estimates, data/processed/population_spain_midyear_5yr.csv
- Foreign-resident population stock (2006-2024) by sex from INE Padrón,
  via data/raw/migration_spain.csv's `stock_nationality` series (Eurostat
  migr_pop1ctz, per-year per-nationality sex-specific rows summed).
"""

import csv
import json
import sys

import pandas as pd

FEMINICIDE_JSON = 'data/raw/feminicidios_delegacion_2003-2026.json'
POPULATION_CSV = 'data/processed/population_spain_midyear_5yr.csv'
MIGRATION_CSV = 'data/raw/migration_spain.csv'
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


def load_total_female_population():
    """Total female population (all ages, summed across age groups) by
    year, from INE Padrón midyear estimates."""
    totals = {}
    with open(POPULATION_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['sex'] != 'female':
                continue
            year = int(row['year'])
            if year not in YEARS:
                continue
            totals[year] = totals.get(year, 0) + int(row['population_july1'])
    return totals


def load_total_male_population():
    """Total male population (all ages, summed across age groups) by
    year, from INE Padrón midyear estimates."""
    totals = {}
    with open(POPULATION_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['sex'] != 'male':
                continue
            year = int(row['year'])
            if year not in YEARS:
                continue
            totals[year] = totals.get(year, 0) + int(row['population_july1'])
    return totals


def load_foreign_stock_by_sex():
    """Per-year foreign-resident stock by sex, summed across all
    nationalities from Eurostat migr_pop1ctz (stock_nationality series).

    Returns dict[year] -> dict['female'|'male'|'all'] -> int.
    """
    df = pd.read_csv(MIGRATION_CSV)
    mask = (
        (df['series'] == 'stock_nationality')
        & (df['age_group'] == 'all')
        & (df['sex'].isin(['female', 'male', 'all']))
    )
    sub = df.loc[mask, ['year', 'sex', 'value']].copy()
    sub['year'] = sub['year'].astype(int)
    sub['value'] = sub['value'].astype(int)
    piv = sub.groupby(['year', 'sex'])['value'].sum().unstack(fill_value=0)
    result = {}
    for year in piv.index:
        if year not in YEARS:
            continue
        result[year] = {
            'female': int(piv.loc[year, 'female']) if 'female' in piv.columns else 0,
            'male': int(piv.loc[year, 'male']) if 'male' in piv.columns else 0,
            'all': int(piv.loc[year, 'all']) if 'all' in piv.columns else 0,
        }
    return result


def estimate_nationality_population(year, total_by_year, foreign_by_sex, sex):
    """
    Population (for a given sex) by origin (Spanish resident vs foreign
    resident) for `year`, from real INE Padrón + Eurostat data.

    total(year)   : INE Padrón midyear population for the given sex, all ages.
    foreign(year) : Eurostat stock_nationality total for the given sex, all
                    nationalities summed, for `year`.
    spanish(year) : total(year) - foreign(year) -- Padrón population counts
                    include foreign residents, they are not additional on
                    top of the total.
    """
    total = total_by_year[year]
    foreign = foreign_by_sex[year][sex]
    spanish = total - foreign

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
    total_female_by_year = load_total_female_population()
    total_male_by_year = load_total_male_population()
    foreign_by_sex = load_foreign_stock_by_sex()

    pop_by_role = {
        'victim': (total_female_by_year, 'female'),
        'perpetrator': (total_male_by_year, 'male'),
    }

    results = []
    for year in YEARS:
        if year not in fem_data or year not in foreign_by_sex:
            continue
        if year not in total_female_by_year or year not in total_male_by_year:
            continue

        for role in ROLES:
            total_by_year, sex = pop_by_role[role]
            pop_data = estimate_nationality_population(
                year, total_by_year, foreign_by_sex, sex)

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
                        f'(high confidence); population: INE Padrón total {sex_label} '
                        f'minus Eurostat migr_pop1ctz foreign-resident {sex_label} stock '
                        f'(stock_nationality series, per-year per-nationality, ~86% of '
                        f'INE ECP total foreign stock)'
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
