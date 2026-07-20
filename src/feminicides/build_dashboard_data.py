"""Build the feminicides.json dashboard data blob.

Reads the consolidated Delegación del Gobierno feminicide dataset + the
computed per-origin rate CSV, returns the dict written to
docs/data/feminicides.json — same shape as before this file was split out
of src/analysis/build_dashboard.py.
"""

import csv
import json

CONF_DELEGACION = "high"


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


def build():
    reports = read_json("data/raw/feminicidios_delegacion_2003-2026.json")["reports"]
    reports = [r for r in reports if r.get("total_victims") is not None]
    reports.sort(key=lambda r: r["year"])

    # National partner/ex-partner homicide timeline.
    timeline = {
        "years": [r["year"] for r in reports],
        "values": [r["total_victims"] for r in reports],
        "confidence": [r.get("confidence") or CONF_DELEGACION for r in reports],
    }

    # Latest year with a regional breakdown → ranked bar / choropleth feed.
    regional = {}
    for r in reversed(reports):
        if r.get("regional"):
            regional = {
                "year": r["year"],
                "rows": [
                    {"label": x["label"], "count": x["count"], "pct": x.get("pct")}
                    for x in r["regional"]
                ],
            }
            break

    # Latest year with victim age × origin detail.
    age_origin = {}
    for r in reversed(reports):
        if r.get("age") and r.get("origin"):
            age_origin = {
                "year": r["year"],
                "age": [
                    {"label": a["label"], "victims": a.get("victim_count"), "perps": a.get("perp_count")}
                    for a in r["age"]
                ],
                "origin": [
                    {"label": o["label"], "victims": o.get("victim_count"), "pct": o.get("victim_pct")}
                    for o in r["origin"]
                ],
            }
            break

    # Latest-year rate per 100k by origin (Spanish resident vs foreign resident).
    rate_rows = read_csv("data/processed/feminicide_rates_2006-2024.csv")
    latest_year = max((num(r["year"]) for r in rate_rows), default=None)
    latest_rows = [r for r in rate_rows if num(r["year"]) == latest_year]
    rates = {
        "year": latest_year,
        "rows": [
            {
                "origin": r["origin"],
                "victims": num(r["victims_count"]),
                "population": num(r["population"]),
                "rate_per_100k": num(r["rate_per_100k"]),
                "ci_lower": num(r["ci_lower"]),
                "ci_upper": num(r["ci_upper"]),
                "confidence": r["confidence"],
            }
            for r in latest_rows
        ],
    }

    return {
        "source": "Delegación del Gobierno contra la Violencia de Género — víctimas mortales por violencia de pareja",
        "source_url": "https://violenciagenero.igualdad.gob.es/",
        "confidence": CONF_DELEGACION,
        "timeline": timeline,
        "regional": regional,
        "age_origin": age_origin,
        "rates_2024": rates,
    }
