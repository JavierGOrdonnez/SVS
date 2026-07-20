"""Build the sexual_crimes.json dashboard data blob.

Reads the MIR Informe JSON + processed evolution/convictions CSVs, returns
the dict written to docs/data/sexual_crimes.json — same shape as before
this file was split out of src/analysis/build_dashboard.py.
"""

import csv
import json
from collections import defaultdict


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
    informe = read_json("data/raw/sexual_crimes_mir_2019-2024.json")["reports"]
    informe.sort(key=lambda r: r["year"])

    # Reported totals + perpetrator-male share, from the MIR Informe.
    totals = {
        "years": [r["year"] for r in informe],
        "total": [r.get("total_count") for r in informe],
        "perp_male_pct": [r.get("perp_male_pct") for r in informe],
        "victims_minor_pct": [r.get("victims_minor_pct") for r in informe],
    }

    # Category trends + Spanish/foreign perpetrator split, from the evolution CSV.
    ev = read_csv("data/processed/sexual_crime_evolution.csv")
    cat, nat = defaultdict(dict), defaultdict(dict)
    for r in ev:
        y = num(r["year"])
        if r["section"] == "category":
            cat[r["series"]][y] = num(r["value"])
        elif r["section"] == "nationality":
            nat[r["series"]][y] = num(r["value"])
    cat_years = sorted({y for s in cat.values() for y in s})
    nat_years = sorted({y for s in nat.values() for y in s})
    categories = {
        "years": cat_years,
        "series": {k: [v.get(y) for y in cat_years] for k, v in cat.items()},
    }
    nationality = {
        "years": nat_years,
        "series": {k: [v.get(y) for y in nat_years] for k, v in nat.items()},
    }

    # Convictions by nationality group (INE table 28716), aggregated across
    # sexual-crime categories per (year, nationality).
    conv_rows = read_csv("data/processed/ine_condenados_28716_sexual_crimes.csv")
    conv = defaultdict(lambda: defaultdict(float))
    for r in conv_rows:
        conv[num(r["year"])][r["nationality_label"]] += num(r["count"]) or 0
    conv_years = sorted(conv)
    conv_groups = sorted({g for y in conv.values() for g in y})
    convictions = {
        "years": conv_years,
        "groups": conv_groups,
        "series": {g: [round(conv[y].get(g, 0)) for y in conv_years] for g in conv_groups},
    }

    return {
        "source": "Ministerio del Interior — Informe sobre delitos contra la libertad sexual; INE Estadística de Condenados (t.28716)",
        "source_url": "https://estadisticasdecriminalidad.ses.mir.es/",
        "confidence": "high",
        "definition_breaks": {2022: "LO 10/2022 (‘Solo sí es sí’) narrowed the rape definition", 2023: "further reform"},
        "totals": totals,
        "categories": categories,
        "nationality": nationality,
        "convictions": convictions,
    }
