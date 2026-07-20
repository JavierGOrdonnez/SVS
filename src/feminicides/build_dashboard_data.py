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

# Canonical age bands (V41) reconciling the legacy 8-band scheme (2003-2005)
# with the modern 10-band scheme (2006+) into one consistent set so the
# timeline chart stacks the same bands across every year. Under-18 bands
# collapse to a single bucket on both sides; the modern schema's three
# oldest bands (61-70/71-84/85+) collapse into legacy's single ">64 años"
# since legacy has no finer resolution to split into — "61 a 70 años"
# folds into ">64 años" rather than "51-64 años" since most of that
# decade (65-70) falls past 64.
CANON_AGE_BANDS = [
    "<18 años", "18-20 años", "21-30 años", "31-40 años",
    "41-50 años", "51-64 años", ">64 años", "No consta",
]
AGE_BAND_REBIN = {
    # modern (2006+)
    "13 a 14 años": "<18 años", "15 a 17 años": "<18 años",
    "18 a 20 años": "18-20 años", "21 a 30 años": "21-30 años",
    "31 a 40 años": "31-40 años", "41 a 50 años": "41-50 años",
    "51 a 60 años": "51-64 años", "61 a 70 años": ">64 años",
    "71 a 84 años": ">64 años", "85 años o más": ">64 años",
    # legacy (2003-2005)
    "<16 años": "<18 años", "16-17 años": "<18 años",
    "18-20 años": "18-20 años", "21-30 años": "21-30 años",
    "31-40 años": "31-40 años", "41-50 años": "41-50 años",
    "51-64 años": "51-64 años", ">64 años": ">64 años",
    "No consta": "No consta",
}


def rebin_age_breakdown(age_list):
    """Re-bucket a report's raw per-year age breakdown into CANON_AGE_BANDS,
    for both victims and perpetrators. A band's `victims`/`perps` value is
    `None` (not 0) when that actor genuinely has no data for it that year
    (e.g. a block failed the V39 reconciliation gate) rather than a real
    zero count."""
    if not age_list:
        return None
    victims = {b: 0 for b in CANON_AGE_BANDS}
    perps = {b: 0 for b in CANON_AGE_BANDS}
    v_present = {b: False for b in CANON_AGE_BANDS}
    p_present = {b: False for b in CANON_AGE_BANDS}
    for a in age_list:
        canon = AGE_BAND_REBIN.get(a["label"])
        if canon is None:
            continue
        if a.get("victim_count") is not None:
            victims[canon] += a["victim_count"]
            v_present[canon] = True
        if a.get("perp_count") is not None:
            perps[canon] += a["perp_count"]
            p_present[canon] = True
    return [
        {
            "label": b,
            "victims": victims[b] if v_present[b] else None,
            "perps": perps[b] if p_present[b] else None,
        }
        for b in CANON_AGE_BANDS if v_present[b] or p_present[b]
    ]


def moving_average(values, window=5):
    """Trailing moving average (uses however many of the last `window`
    years are available, so the first `window-1` points use a shorter
    span rather than staying null)."""
    out = []
    for i in range(len(values)):
        span = values[max(0, i - window + 1):i + 1]
        out.append(round(sum(span) / len(span), 2))
    return out


def build():
    reports = read_json("data/raw/feminicidios_delegacion_2003-2026.json")["reports"]
    reports.sort(key=lambda r: r["year"])

    # National partner/ex-partner homicide timeline, 2003-present.
    values = [r["total_victims"] for r in reports]
    timeline = {
        "years": [r["year"] for r in reports],
        "values": values,
        "values_ma5": moving_average(values),
        "age_breakdown": [rebin_age_breakdown(r.get("age")) for r in reports],
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
