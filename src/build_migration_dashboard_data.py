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

COUNTRY_NAMES = {
    "CO": "Colombia",
    "MA": "Morocco",
    "RO": "Romania",
    "IT": "Italy",
    "GB": "United Kingdom",
    "VE": "Venezuela",
    "PE": "Peru",
    "CN": "China",
    "HN": "Honduras",
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


def main():
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
    s6 = {
        "years": [int(r["year"]) for r in stock_nat],
        "foreign_nationality": [int(r["value"]) for r in stock_nat],
        "foreign_born_years": [int(r["year"]) for r in stock_born],
        "foreign_born": [int(r["value"]) for r in stock_born],
    }

    blob = {
        "annual_inflow": s1,
        "origin_composition": s2,
        "sex_split": s3,
        "age_band_over_time": s4,
        "age_profile_latest": s5,
        "stock_trend": s6,
    }

    js = "const MIGRATION = " + json.dumps(blob, ensure_ascii=False, separators=(",", ":")) + ";\n"
    sys.stdout.write(js)


if __name__ == "__main__":
    main()
