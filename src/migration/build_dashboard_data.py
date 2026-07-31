"""Emit JS constants for the migration tab of docs/index.html.

Reads data/raw/migration_spain.csv and writes a self-contained JS block to
stdout that the dashboard can paste/include verbatim — same pattern as
build_dashboard_data.py for the mortality tab (single static file, no
fetch/CORS/build step).
"""

import csv
import json
import sys
from collections import defaultdict

CSV_PATH = "data/raw/migration_spain.csv"
POPULATION_CSV = "data/processed/population_spain_midyear_5yr.csv"

# nationality -> display region, for the T68 stock-by-region panel and the
# T69/T70 age-pyramid regional breakdown. Covers all 50 non-ES codes carried
# by `stock_nationality` (T43/T44/T66); AT has no Eurostat migr_pop1ctz rows
# (never downloaded) so it contributes 0 wherever it'd otherwise appear.
REGION_MAP = {
    # Africa
    "MA": "Africa", "DZ": "Africa", "SN": "Africa", "NG": "Africa", "ML": "Africa",
    "GQ": "Africa", "GN": "Africa", "GH": "Africa", "GM": "Africa",
    # Latin America
    "CO": "Latin America", "VE": "Latin America", "PE": "Latin America",
    "HN": "Latin America", "AR": "Latin America", "EC": "Latin America",
    "PY": "Latin America", "BR": "Latin America", "BO": "Latin America",
    "CU": "Latin America", "NI": "Latin America", "DO": "Latin America",
    "CL": "Latin America", "MX": "Latin America", "UY": "Latin America",
    # Anglo
    "UK": "Anglo", "US": "Anglo",
    # EU
    "RO": "EU", "IT": "EU", "DE": "EU", "FR": "EU", "PT": "EU", "BG": "EU",
    "NL": "EU", "PL": "EU", "SE": "EU", "IE": "EU", "BE": "EU", "DK": "EU",
    "FI": "EU", "LT": "EU", "AT": "EU",
    # Non-EU Europe
    "UA": "Non-EU Europe", "RU": "Non-EU Europe", "CH": "Non-EU Europe",
    "NO": "Non-EU Europe", "MD": "Non-EU Europe",
    # Asia
    "CN": "Asia", "PK": "Asia", "IN": "Asia", "BD": "Asia", "PH": "Asia",
}
REGIONS = ["Africa", "Latin America", "Anglo", "EU", "Non-EU Europe", "Asia"]

# Shared 17-band scale for both age pyramids (T69/T70), fine 5yr bands all
# the way from 0-4 to 80+ (Eurostat migr_pop1ctz publishes Y_LT5/Y5-9 at the
# young end and Y60-64...Y80-84 + a Y_GE85 aggregate at the old end;
# population_spain_midyear_5yr.csv has matching bins throughout).
PYRAMID_AGES = [
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34",
    "35-39", "40-44", "45-49", "50-54", "55-59", "60-64",
    "65-69", "70-74", "75-79", "80+",
]

COUNTRY_NAMES = {
    "CO": "Colombia",
    "MA": "Morocco",
    "RO": "Romania",
    "IT": "Italy",
    "GB": "United Kingdom",  # legacy flow-series code (pre-2018 EU convention)
    "VE": "Venezuela",
    "PE": "Peru",
    "CN": "China",
    "HN": "Honduras",
    # T72: rest of REGION_MAP's 50 stock_nationality codes (Eurostat's own
    # "UK", not the legacy flow-series "GB" above, for the same country).
    "DZ": "Algeria", "SN": "Senegal", "NG": "Nigeria", "ML": "Mali",
    "GQ": "Equatorial Guinea", "GN": "Guinea", "GH": "Ghana", "GM": "Gambia",
    "AR": "Argentina", "EC": "Ecuador", "PY": "Paraguay", "BR": "Brazil",
    "BO": "Bolivia", "CU": "Cuba", "NI": "Nicaragua", "DO": "Dominican Republic",
    "CL": "Chile", "MX": "Mexico", "UY": "Uruguay",
    "UK": "United Kingdom", "US": "United States",
    "DE": "Germany", "FR": "France", "PT": "Portugal", "BG": "Bulgaria",
    "NL": "Netherlands", "PL": "Poland", "SE": "Sweden", "IE": "Ireland",
    "BE": "Belgium", "DK": "Denmark", "FI": "Finland", "LT": "Lithuania",
    "AT": "Austria",
    "UA": "Ukraine", "RU": "Russia", "CH": "Switzerland", "NO": "Norway",
    "MD": "Moldova",
    "PK": "Pakistan", "IN": "India", "BD": "Bangladesh", "PH": "Philippines",
}

# Countries with the longest, most continuous year-coverage in the source
# rows (>= 14 years each) — chosen for a stable stacked-series legend.
TOP_ORIGINS = ["CO", "MA", "RO", "IT", "GB", "VE", "PE"]

AGE_BANDS = ["0-14", "15-29", "30-44", "45-64", "65+"]

DETAILED_AGE_ORDER = (
    ["0-4", "5-9", "10-14"]
    + [f"{x}-{x+4}" for x in range(15, 90, 5)]
    + ["90+"]
)


def load_rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _pyramid_band_value(totals, key_prefix, age):
    """One pyramid age-band's value from a {(*key_prefix, age_group): value}
    totals dict, deriving the 80+ aggregate as `80-84 plus 85+` (Eurostat's
    oldest 5yr band is 80-84, with Y_GE85 as the open-ended top). Every
    other band (including 0-4/5-9) is a real Eurostat/population bin, no
    further derivation needed."""
    if age == "80+":
        return totals[(*key_prefix, "80-84")] + totals[(*key_prefix, "85+")]
    return totals[(*key_prefix, age)]


TOP_N_PER_REGION = 7  # T72: drill-down bar chart shows this many named countries + "Other"


def _region_country_breakdown(by_country_year, region_codes, years):
    """T72: one region's per-country stock, ranked by latest-year value,
    top TOP_N_PER_REGION named individually + the rest summed into "Other"
    (kept as a single bucket rather than showing all — Latin America/EU
    have 15 constituent countries each, more than PALETTE's 8 colors)."""
    latest_year = years[-1]
    ranked = sorted(region_codes, key=lambda c: by_country_year[c].get(latest_year, 0), reverse=True)
    top, rest = ranked[:TOP_N_PER_REGION], ranked[TOP_N_PER_REGION:]
    series = {
        COUNTRY_NAMES.get(c, c): [by_country_year[c].get(y, 0) for y in years]
        for c in top
    }
    if rest:
        series["Other"] = [sum(by_country_year[c].get(y, 0) for c in rest) for y in years]
    return {"countries": list(series.keys()), "series": series}


def _total_population_by_year():
    """INE Padrón midyear total population (all residents, Spanish + foreign),
    summed across age bands, per year. Backs both _spain_stock_series() below
    and _stock_trend()'s foreign_pct_of_total. Only runs through 2024."""
    pop_rows = load_rows(POPULATION_CSV)
    total_pop_by_year = defaultdict(int)
    for r in pop_rows:
        if r["sex"] != "all":
            continue
        total_pop_by_year[int(r["year"])] += int(r["population_july1"])
    return total_pop_by_year


def _spain_stock_series(years, by_region_year, total_pop_by_year):
    """Spanish-national population per year, same subtraction approach as
    T70's _spanish_age_pyramid (INE Padrón midyear total minus foreign
    stock) but summed as a single yearly total rather than by age band, so
    mi-stock-region can carry a `spain` reference line like the two
    sexual-crimes drill panels already do (V44-adjacent: derived from the
    same rows the region series themselves sum, so it's consistent with
    them, not an independent estimate). population_spain_midyear_5yr.csv
    only runs through 2024, one year short of stock_nationality's 2025 —
    left as a genuine null gap for any year without population data rather
    than carrying the last known total forward."""
    def spain_value(year):
        if year not in total_pop_by_year:
            return None
        foreign_total = sum(by_region_year[region].get(year, 0) for region in REGIONS)
        return total_pop_by_year[year] - foreign_total

    return [spain_value(y) for y in years]


def _stock_by_region(rows):
    """T68: foreign-national stock summed per display region, over time.
    T72: also carries each region's per-country breakdown (by_country) for
    the mi-stock-region drill-down panel."""
    stock_all = [
        r for r in rows
        if r["series"] == "stock_nationality"
        and r["age_group"] == "all" and r["sex"] == "all"
    ]
    years = sorted({int(r["year"]) for r in stock_all})
    by_region_year = defaultdict(lambda: defaultdict(int))
    by_country_year = defaultdict(lambda: defaultdict(int))
    for r in stock_all:
        region = REGION_MAP.get(r["nationality"])
        if region is None:
            continue
        year = int(r["year"])
        by_region_year[region][year] += int(r["value"])
        by_country_year[r["nationality"]][year] += int(r["value"])

    codes_by_region = defaultdict(list)
    for code, region in REGION_MAP.items():
        codes_by_region[region].append(code)

    return {
        "years": years,
        "regions": REGIONS,
        "spain": _spain_stock_series(years, by_region_year, _total_population_by_year()),
        "by_country": {
            region: _region_country_breakdown(by_country_year, codes_by_region[region], years)
            for region in REGIONS
        },
        "series": {
            region: [by_region_year[region].get(y, 0) for y in years]
            for region in REGIONS
        },
    }


def _stock_age_pyramid(rows, year):
    """T69: foreign-national age x sex pyramid, overall + per region, for
    the given year (latest year with matching Spanish-population coverage,
    so it lines up with the T70 Spanish pyramid on the same axis)."""
    stock = [
        r for r in rows
        if r["series"] == "stock_nationality" and int(r["year"]) == year
        and r["sex"] in ("male", "female") and r["nationality"] in REGION_MAP
    ]
    totals = defaultdict(int)  # (region, sex, age_group) -> value
    for r in stock:
        region = REGION_MAP[r["nationality"]]
        totals[(region, r["sex"], r["age_group"])] += int(r["value"])

    def band_values(region, sex):
        return [_pyramid_band_value(totals, (region, sex), age) for age in PYRAMID_AGES]

    def all_band_values(sex):
        return [
            sum(_pyramid_band_value(totals, (region, sex), age) for region in REGIONS)
            for age in PYRAMID_AGES
        ]

    return {
        "year": year,
        "ages": PYRAMID_AGES,
        "male": all_band_values("male"),
        "female": all_band_values("female"),
        "regions": {
            region: {"male": band_values(region, "male"), "female": band_values(region, "female")}
            for region in REGIONS
        },
    }


# population_spain_midyear_5yr.csv's native age bins -> the shared 17-band
# pyramid scale (PYRAMID_AGES).
POP_TO_PYRAMID_AGE = {
    "<1": "0-4", "1-4": "0-4", "5-9": "5-9",
    "10-14": "10-14", "15-19": "15-19", "20-24": "20-24", "25-29": "25-29",
    "30-34": "30-34", "35-39": "35-39", "40-44": "40-44", "45-49": "45-49",
    "50-54": "50-54", "55-59": "55-59", "60-64": "60-64",
    "65-69": "65-69", "70-74": "70-74", "75-79": "75-79",
    "80-84": "80+", "85-89": "80+", "90-94": "80+", "95+": "80+",
}


def _spanish_age_pyramid(rows, year):
    """T70: Spanish-national age x sex pyramid = total population (INE
    midyear estimate) minus foreign stock (Eurostat), same 17-band scale
    and year as the T69 foreign pyramid."""
    pop_rows = load_rows(POPULATION_CSV)
    pop_totals = defaultdict(int)  # (sex, pyramid_age) -> value
    for r in pop_rows:
        if int(r["year"]) != year or r["sex"] not in ("male", "female"):
            continue
        pyramid_age = POP_TO_PYRAMID_AGE.get(r["age_group"])
        if pyramid_age is None:
            continue
        pop_totals[(r["sex"], pyramid_age)] += int(r["population_july1"])

    foreign_stock = [
        r for r in rows
        if r["series"] == "stock_nationality" and int(r["year"]) == year
        and r["sex"] in ("male", "female") and r["nationality"] in REGION_MAP
    ]
    foreign_totals = defaultdict(int)  # (sex, age_group) -> value
    for r in foreign_stock:
        foreign_totals[(r["sex"], r["age_group"])] += int(r["value"])

    def spanish_values(sex):
        return [
            pop_totals[(sex, age)] - _pyramid_band_value(foreign_totals, (sex,), age)
            for age in PYRAMID_AGES
        ]

    return {
        "year": year,
        "ages": PYRAMID_AGES,
        "male": spanish_values("male"),
        "female": spanish_values("female"),
    }


def build():
    """Return the migration-tab data blob (also reused by build_dashboard.py)."""
    rows = load_rows(CSV_PATH)
    flow = [r for r in rows if r["series"] == "flow_immigration_from_abroad"]

    # 1. Annual total inflow, 2000-2024 — flag the 2008 EVR -> EMCR break
    totals = [
        r for r in flow
        if r["sex"] == "all" and r["age_group"] == "all"
        and r["country_of_origin"] == "all" and r["nationality"] == "all"
    ]
    totals.sort(key=lambda r: int(r["year"]))
    s1 = {
        "years": [int(r["year"]) for r in totals],
        "values": [int(r["value"]) for r in totals],
        "sources": [r["source_name"] for r in totals],
    }

    # 2. Origin-country composition of inflow, 2008-2024 (top continuous-coverage origins)
    origin_rows = [
        r for r in flow
        if r["country_of_origin"] in TOP_ORIGINS
        and r["sex"] == "all" and r["age_group"] == "all"
    ]
    origin_years = sorted({int(r["year"]) for r in origin_rows})
    by_country_year = {(r["country_of_origin"], int(r["year"])): int(r["value"]) for r in origin_rows}
    s2 = {
        "years": origin_years,
        "origins": [COUNTRY_NAMES[c] for c in TOP_ORIGINS],
        "series": {
            COUNTRY_NAMES[c]: [by_country_year.get((c, y)) for y in origin_years]
            for c in TOP_ORIGINS
        },
    }

    # 3. Sex split of inflow over time, 2008-2024
    sex_rows = [
        r for r in flow
        if r["sex"] in ("male", "female") and r["age_group"] == "all"
        and r["country_of_origin"] == "all"
    ]
    sex_years = sorted({int(r["year"]) for r in sex_rows})
    by_sex_year = {(r["sex"], int(r["year"])): int(r["value"]) for r in sex_rows}
    s3 = {
        "years": sex_years,
        "male": [by_sex_year.get(("male", y)) for y in sex_years],
        "female": [by_sex_year.get(("female", y)) for y in sex_years],
    }

    # 4. Broad age-band composition of inflow over time, 2008-2024
    age_rows = [
        r for r in flow
        if r["age_group"] in AGE_BANDS and r["sex"] == "all"
        and r["country_of_origin"] == "all"
    ]
    age_years = sorted({int(r["year"]) for r in age_rows})
    by_band_year = {(r["age_group"], int(r["year"])): int(r["value"]) for r in age_rows}
    s4 = {
        "years": age_years,
        "bands": AGE_BANDS,
        "series": {
            band: [by_band_year.get((band, y)) for y in age_years]
            for band in AGE_BANDS
        },
    }

    # 5. Detailed 5-year age profile of inflow, latest year with that breakdown (2024)
    detailed = [
        r for r in flow
        if r["sex"] == "all" and r["country_of_origin"] == "all"
        and r["age_group"] not in ("all", *AGE_BANDS)
    ]
    detail_year = max(int(r["year"]) for r in detailed)
    detail_latest = {r["age_group"]: int(r["value"]) for r in detailed if int(r["year"]) == detail_year}
    s5 = {
        "year": detail_year,
        "ages": DETAILED_AGE_ORDER,
        "values": [detail_latest.get(a, 0) for a in DETAILED_AGE_ORDER],
    }

    # 6. Foreign-population stock trend — nationality (annual) + foreign-born (sparse snapshots)
    stock_nat = sorted(
        (r for r in rows if r["series"] == "stock_foreign_nationality"
         and r["sex"] == "all" and r["country_of_origin"] == "all"),
        key=lambda r: int(r["year"]),
    )
    stock_born = sorted(
        (r for r in rows if r["series"] == "stock_foreign_born"),
        key=lambda r: int(r["year"]),
    )
    # foreign_nationality's own share of total resident population, per year
    # (INE Padrón midyear total) — the normalized companion to that raw
    # count: is the *share* of foreign residents rising, not just the count.
    # Only available through 2024 (population_spain_midyear_5yr.csv's last
    # year); 2025 is a genuine null gap, not carried forward.
    total_pop_by_year = _total_population_by_year()
    s6 = {
        "years": [int(r["year"]) for r in stock_nat],
        "foreign_nationality": [int(r["value"]) for r in stock_nat],
        "foreign_pct_of_total": [
            round(int(r["value"]) / total_pop_by_year[int(r["year"])] * 100, 2)
            if int(r["year"]) in total_pop_by_year else None
            for r in stock_nat
        ],
        "foreign_born_years": [int(r["year"]) for r in stock_born],
        "foreign_born": [int(r["value"]) for r in stock_born],
    }

    # 7. Stock by region over time (T68)
    s7 = _stock_by_region(rows)

    # 8/9. Age pyramids (T69/T70) — share the latest year covered by the
    # Spanish population estimates (2024) so both charts sit on the same year.
    pyramid_year = max(int(r["year"]) for r in load_rows(POPULATION_CSV))
    s8 = _stock_age_pyramid(rows, pyramid_year)
    s9 = _spanish_age_pyramid(rows, pyramid_year)

    return {
        "annual_inflow": s1,
        "origin_composition": s2,
        "sex_split": s3,
        "age_band_over_time": s4,
        "age_profile_latest": s5,
        "stock_trend": s6,
        "stock_by_region": s7,
        "stock_age_pyramid": s8,
        "stock_age_pyramid_es": s9,
    }


def main():
    # Legacy CLI: emit as a JS const block on stdout.
    blob = build()
    js = "const MIGRATION = " + json.dumps(blob, ensure_ascii=False, separators=(",", ":")) + ";\n"
    sys.stdout.write(js)


if __name__ == "__main__":
    main()
