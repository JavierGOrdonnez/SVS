"""Build the hate_crimes.json and cohort_tenure.json dashboard data blobs.

Reads the MIR "Delitos de Odio" JSON + the cohort-tenure test CSVs, returns
the dicts written to docs/data/hate_crimes.json and
docs/data/cohort_tenure.json — same shape as before this file was split
out of src/analysis/build_dashboard.py.
"""

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.parsers.mir_parser import classify_odio_category


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


def _nationality_block(csv_path):
    """Read a hate_crimes_ses_nacionalidad_*_summary CSV -> {years, overall,
    by_category}, keyed by the same normalized category keys as `categories`
    (via classify_odio_category), so app.js can share one category legend
    across the typology and nationality charts."""
    rows = read_csv(csv_path)
    years = sorted({int(r["anyo"]) for r in rows})

    overall = {"espana": {}, "foreign": {}, "pct_spanish": {}}
    by_cat = defaultdict(lambda: {"espana": {}, "foreign": {}, "pct_spanish": {}})
    for r in rows:
        year = int(r["anyo"])
        espana, foreign, pct = num(r["espana"]), num(r["foreign"]), num(r["pct_spanish"])
        if r["ambito"] == "TOTAL ámbito":
            overall["espana"][year] = espana
            overall["foreign"][year] = foreign
            overall["pct_spanish"][year] = pct
        else:
            key = classify_odio_category(r["ambito"]) or r["ambito"]
            by_cat[key]["espana"][year] = espana
            by_cat[key]["foreign"][year] = foreign
            by_cat[key]["pct_spanish"][year] = pct

    return {
        "years": years,
        "overall": {k: [v.get(y) for y in years] for k, v in overall.items()},
        "categories": {
            cat: {k: [v.get(y) for y in years] for k, v in series.items()}
            for cat, series in by_cat.items()
        },
    }


def build_hate_crimes():
    reports = read_json("data/raw/hate_crimes_mir_2016-2021_2023.json")["reports"]
    reports.sort(key=lambda r: r["year"])
    years = [r["year"] for r in reports]  # note: 2022 absent (publication gap)

    totals = {"years": years, "total": [r.get("total_count") for r in reports]}

    # Per-category time series (exclude the aggregate 'total_delitos' row).
    by_cat = defaultdict(dict)
    for r in reports:
        for c in r.get("categories", []):
            if c["category"] == "total_delitos":
                continue
            by_cat[c["category"]][r["year"]] = c.get("count")
    # Rank categories by their latest-year magnitude for a stable legend.
    latest = years[-1]
    ranked = sorted(by_cat, key=lambda c: -(by_cat[c].get(latest) or 0))
    categories = {
        "years": years,
        "categories": ranked,
        "series": {c: [by_cat[c].get(y) for y in years] for c in ranked},
    }

    nationality = {
        "years": [2021, 2022, 2023, 2024],
        "detainees": _nationality_block("data/raw/hate_crimes_ses_nacionalidad_detenidos_summary_2021-2024.csv"),
        "victims": _nationality_block("data/raw/hate_crimes_ses_nacionalidad_victimas_summary_2021-2024.csv"),
    }

    return {
        "source": "Ministerio del Interior — Informe sobre la evolución de los delitos de odio en España",
        "source_url": "https://www.interior.gob.es/opencms/es/servicios-al-ciudadano/delitos-de-odio/",
        "confidence": "high",
        "gap_year": 2022,
        "definition_breaks": {
            2017: "‘discapacidad’ → ‘diversidad funcional’ methodology change (structural −91%)",
            2019: "‘antigitanismo’ category added",
        },
        "totals": totals,
        "categories": categories,
        "nationality": nationality,
        "nationality_source": "Portal Estadístico de Criminalidad (SES/MIR), tablas 06019 (detenidos/investigados) y 06013 (victimizaciones), nivel nacional",
        "nationality_source_url": "https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/publicaciones.html",
        "nationality_caveat": "Solo 2021-2024 (el sistema de consulta del portal no tiene datos anteriores para delitos de odio, ni siquiera para series sin desglose de nacionalidad). Detenidos/investigados no equivale a condenados: no existe una serie oficial de condenas por delito de odio y nacionalidad.",
    }


def build_cohort_tenure():
    def call(row):
        return (row.get("hypothesis_call") or "").strip()

    # Test A — whole-group rate ratio vs pre-2022 baseline.
    period = read_csv("data/processed/cohort_tenure_period_test.csv")
    test_a = defaultdict(lambda: {"periods": [], "rate_ratio": [], "p_value": [], "call": []})
    for r in period:
        g = test_a[r["group"]]
        g["periods"].append(r["test_period"])
        g["rate_ratio"].append(num(r["rate_ratio"]))
        g["p_value"].append(num(r["p_value"]))
        g["call"].append(call(r))

    # Test C — share of all identified perpetrators vs baseline.
    share = read_csv("data/processed/cohort_share_test.csv")
    test_c = defaultdict(lambda: {"periods": [], "share_baseline_pct": [], "share_test_pct": [], "p_value": [], "call": []})
    for r in share:
        g = test_c[r["group"]]
        g["periods"].append(r["test_period"])
        g["share_baseline_pct"].append(num(r["share_baseline_pct"]))
        g["share_test_pct"].append(num(r["share_test_pct"]))
        g["p_value"].append(num(r["p_value"]))
        g["call"].append(call(r))

    return {
        "source": "reports/cohort_tenure_analysis.md — Poisson two-sample tests on MIR crime counts vs Eurostat population denominators",
        "confidence": "medium",
        "caveat": "Associative, descriptive tests. Real 5-yr age×sex×nationality denominators exist only for Morocco and Algeria; other groups use share tests only.",
        "test_a_rate_ratio": dict(test_a),
        "test_c_share": dict(test_c),
    }
