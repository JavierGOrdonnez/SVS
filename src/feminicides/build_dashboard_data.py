"""Build the feminicides.json dashboard data blob.

Reads the consolidated Delegación del Gobierno feminicide dataset + the
computed per-origin rate CSV, returns the dict written to
docs/data/feminicides.json — same shape as before this file was split out
of src/analysis/build_dashboard.py.
"""

import csv
import json

CONF_DELEGACION = "high"

# 2025 is the last fully consolidated year; 2026 is a partial year in
# progress. Bump this constant manually each January once the prior year's
# report is finalized.
PROVISIONAL_YEAR = 2026


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def num(x):
    """Parse an int/float cell, tolerating '' and trailing '.0'."""
    if x is None or x == "":
        return None
    try:
        f = float(x)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None


# Static, unsourced context markers for the timeline — general knowledge,
# not independently verified against a primary source in this repo.
MILESTONES = [
    {"year": 2004, "label": "LO 1/2004 (Ley Integral)"},
    {"year": 2007, "label": "VioGen launch"},
    {"year": 2017, "label": "Pacto de Estado"},
    {"year": 2021, "label": "LO 8/2021 (infancia)"},
    {"year": 2022, "label": "LO 10/2022 (garantía integral)"},
]


def build():
    reports = read_json("data/raw/feminicidios_delegacion_2003-2026.json")["reports"]
    reports.sort(key=lambda r: r["year"])

    # National partner/ex-partner homicide timeline, 2003-present.
    timeline = {
        "years": [r["year"] for r in reports],
        "values": [r["total_victims"] for r in reports],
        "age_breakdown": [
            [{"label": a["label"], "victims": a.get("victim_count")} for a in r["age"]]
            if r.get("age") else None
            for r in reports
        ],
        "has_age_breakdown": [bool(r.get("age")) for r in reports],
        "provisional": [r["year"] == PROVISIONAL_YEAR for r in reports],
        # Display-only override: the user has manually verified 2003-2026,
        # so the chart shows uniform "high" confidence regardless of each
        # report's own (lower, legacy-format) confidence field. The real
        # nuance — 2003-2005 are secondary-source figures — lives in the
        # dashboard's caveat list, not here.
        "confidence": [CONF_DELEGACION for _ in reports],
    }

    # Victim + perpetrator rate per 100k by origin (Spanish resident vs
    # foreign resident), full 2006-2024 series (not just the latest year).
    rate_rows = read_csv("data/processed/feminicide_rates_2006-2024.csv")
    years = sorted({num(r["year"]) for r in rate_rows})
    rates = {
        "years": years,
        "latest_year": years[-1] if years else None,
        "rows": [
            {
                "year": num(r["year"]),
                "origin": r["origin"],
                "role": r["role"],
                "count": num(r["count"]),
                "population": num(r["population"]),
                "rate_per_100k": num(r["rate_per_100k"]),
                "ci_lower": num(r["ci_lower"]),
                "ci_upper": num(r["ci_upper"]),
                "confidence": r["confidence"],
            }
            for r in rate_rows
        ],
    }

    return {
        "source": "Delegación del Gobierno contra la Violencia de Género — víctimas mortales por violencia de pareja",
        "source_url": "https://violenciagenero.igualdad.gob.es/",
        "confidence": CONF_DELEGACION,
        "timeline": timeline,
        "rates": rates,
        "milestones": MILESTONES,
    }
