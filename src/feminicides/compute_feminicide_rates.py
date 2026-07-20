#!/usr/bin/env python3
"""
Compute per-origin feminicide rates with 95% confidence intervals, 2006-2024.

Data sources:
- Feminicide counts (2006-2024) from Delegación del Gobierno (T19/T20 output),
  data/raw/feminicidios_delegacion_2003-2026.json
- Total female population (2006-2024) from INE Padrón midyear estimates,
  data/processed/population_spain_midyear_5yr.csv
- Foreign-resident population stock (2006-2024) from INE Padrón, via
  data/raw/migration_spain.csv's `stock_foreign_nationality` series; see
  foreign_female_share() for how the Spanish/foreign split is derived.
"""

import csv
import json
import math

FEMINICIDE_JSON = 'data/raw/feminicidios_delegacion_2003-2026.json'
POPULATION_CSV = 'data/processed/population_spain_midyear_5yr.csv'
MIGRATION_CSV = 'data/raw/migration_spain.csv'
OUTPUT_CSV = 'data/processed/feminicide_rates_2006-2024.csv'

YEARS = range(2006, 2025)  # 2006-2024: T19's "modern-format" PDF coverage,
                           # capped by population_spain_midyear_5yr.csv (through 2024)

ORIGIN_LABELS = {'españa': 'España', 'otro_pais': 'Otro país'}


def poisson_ci_95(count):
    """Approximate 95% CI for a Poisson count using the normal (Wald)
    approximation: count ± 1.96·sqrt(count) -- not an exact Poisson CI
    (e.g. Garwood). Returns the conventional "rule of three" upper bound
    (0, 3.689) when count=0, where the normal approximation is degenerate.
    """
    if count == 0:
        return (0, 3.689)  # Poisson rule of 3

    lower = max(0, count - 1.96 * math.sqrt(count))
    upper = count + 1.96 * math.sqrt(count)
    return (lower, upper)


def load_feminicide_data():
    """Load feminicide victim counts by origin for each year in YEARS."""
    with open(FEMINICIDE_JSON, encoding='utf-8') as f:
        dataset = json.load(f)

    data = {}
    for report in dataset['reports']:
        year = report['year']
        if year not in YEARS:
            continue
        data[year] = {entry['label']: entry['victim_count'] for entry in report['origin']}
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


def load_foreign_stock_total():
    """Total foreign-nationality resident stock (both sexes) by year, from
    INE Padrón via migration_spain.csv's stock_foreign_nationality series."""
    totals = {}
    with open(MIGRATION_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row['series'] != 'stock_foreign_nationality'
                    or row['nationality'] != 'foreign'
                    or row['sex'] != 'all' or row['age_group'] != 'all'):
                continue
            year = int(row['year'])
            if year not in YEARS:
                continue
            totals[year] = int(row['value'])
    return totals


def foreign_female_share():
    """
    Female share of the foreign-resident stock.

    migration_spain.csv's stock_foreign_nationality series only carries a
    sex breakdown for 2025 (female=3,423,139 / total=6,911,971 -> 0.4952);
    every other year only has the sex='all' total. That single ratio is
    applied as a constant to every 2006-2024 year below -- a documented
    estimate, not a per-year measurement (see SPEC.md §B for the bug this
    replaces, and T24 in SPEC-feminicides.md for the assumption's scope).
    """
    female = total = None
    with open(MIGRATION_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if (row['series'] == 'stock_foreign_nationality'
                    and row['nationality'] == 'foreign'
                    and row['age_group'] == 'all' and row['year'] == '2025'):
                if row['sex'] == 'female':
                    female = int(row['value'])
                elif row['sex'] == 'all':
                    total = int(row['value'])
    if female is None or total is None:
        raise ValueError(
            f"Could not find 2025 sex-disaggregated stock_foreign_nationality "
            f"rows in {MIGRATION_CSV}"
        )
    return female / total


def estimate_nationality_population(year, total_female_by_year, foreign_stock_by_year, female_share):
    """
    Female population by origin (Spanish resident vs foreign resident) for
    `year`, from real INE Padrón data.

    This replaces a prior circular implementation that back-calculated
    "population" from an assumed feminicide rate (victims ÷ assumed rate)
    and then reported that same assumed rate back as if it had been
    independently computed from population data (see SPEC.md §B).

    total_female(year)   : INE Padrón midyear female population, all ages.
    foreign_female(year) : stock_foreign_nationality total (both sexes) for
                           `year`, scaled by the constant female_share.
    spanish_female(year) : total_female(year) - foreign_female(year) --
                           Padrón population counts include foreign
                           residents, they are not additional on top of the
                           total.
    """
    total_female = total_female_by_year[year]
    foreign_female = foreign_stock_by_year[year] * female_share
    spanish_female = total_female - foreign_female

    return {
        'españa': spanish_female,
        'otro_pais': foreign_female,
        'total': total_female,
    }


def compute_rates():
    """Compute feminicide rates per 100k population with 95% CIs, for every
    year in YEARS that has both a feminicide report and population data."""
    fem_data = load_feminicide_data()
    total_female_by_year = load_total_female_population()
    foreign_stock_by_year = load_foreign_stock_total()
    female_share = foreign_female_share()

    results = []
    for year in YEARS:
        if year not in fem_data or year not in total_female_by_year or year not in foreign_stock_by_year:
            continue

        pop_data = estimate_nationality_population(
            year, total_female_by_year, foreign_stock_by_year, female_share)

        for origin in ['españa', 'otro_pais']:
            count = fem_data[year].get(ORIGIN_LABELS[origin], 0)
            pop = pop_data[origin]

            # Rate per 100,000
            rate_per_100k = (count / pop) * 100_000 if pop > 0 else 0

            # 95% CI for count
            ci_lower, ci_upper = poisson_ci_95(count)

            # Convert CI bounds to rates
            ci_lower_rate = (ci_lower / pop) * 100_000 if pop > 0 else 0
            ci_upper_rate = (ci_upper / pop) * 100_000 if pop > 0 else 0

            results.append({
                'year': year,
                'origin': origin,
                'victims_count': count,
                'population': int(pop),
                'rate_per_100k': round(rate_per_100k, 2),
                'ci_lower': round(ci_lower_rate, 2),
                'ci_upper': round(ci_upper_rate, 2),
                'confidence': 'medium',
                'notes': (
                    f'{origin} {year} — victims: Delegación del Gobierno (high '
                    'confidence); population: INE Padrón total female minus '
                    'estimated foreign-resident female stock (medium confidence, '
                    'constant 2025 female-share ratio applied -- see '
                    'foreign_female_share())'
                ),
            })

    return results


def write_output(results):
    """Write results to CSV."""
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['year', 'origin', 'victims_count', 'population', 'rate_per_100k',
                     'ci_lower', 'ci_upper', 'confidence', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Rates written to {OUTPUT_CSV}")

    # Print summary for the latest year only
    latest_year = max(r['year'] for r in results)
    for r in results:
        if r['year'] != latest_year:
            continue
        print(f"\n{r['year']} {r['origin'].upper()}")
        print(f"  Victims: {r['victims_count']}")
        print(f"  Population: {r['population']:,}")
        print(f"  Rate: {r['rate_per_100k']}/100k (95% CI: {r['ci_lower']}-{r['ci_upper']})")


if __name__ == '__main__':
    rates = compute_rates()
    write_output(rates)
