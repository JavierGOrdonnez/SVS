"""Generate the dashboard data layer: docs/data/*.json.

One orchestrator that reads the project's processed CSVs and nested raw JSON
and emits one clean, fetch-ready JSON file per analytical domain. The web
dashboard (docs/index.html) fetches these at runtime, so there is no more
hand-copied inline data and the GitHub-Pages fetch paths resolve correctly
(files live under docs/data/, the Pages root).

Run:  uv run python src/build_dashboard.py
"""

import csv
import json
import os
from collections import defaultdict

import build_dashboard_data as mortality_mod
import build_migration_dashboard_data as migration_mod

OUT_DIR = os.path.join("docs", "data")

# Confidence tier for whole domains where the source doc is uniform.
CONF_DELEGACION = "high"


# ── generic helpers ──────────────────────────────────────────
def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write(name, blob):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(blob, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  wrote {path}  ({os.path.getsize(path):,} bytes)")


def num(x):
    """Parse an int/float cell, tolerating '' and trailing '.0'."""
    if x is None or x == "":
        return None
    try:
        f = float(x)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None


# ── feminicides ──────────────────────────────────────────────
def build_feminicides():
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

    # 2024 rate per 100k by origin (Spanish-born vs foreign-born).
    rate_rows = read_csv("data/processed/feminicide_rates_2024.csv")
    rates = {
        "year": num(rate_rows[0]["year"]) if rate_rows else None,
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
            for r in rate_rows
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


# ── sexual crimes ────────────────────────────────────────────
def build_sexual_crimes():
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


# ── hate crimes ──────────────────────────────────────────────
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
    }


# ── migration cohort / tenure tests ──────────────────────────
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


# ── orchestrator ─────────────────────────────────────────────
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"Building dashboard data -> {OUT_DIR}/")
    write("mortality.json", mortality_mod.build())
    write("migration.json", migration_mod.build())
    write("feminicides.json", build_feminicides())
    write("sexual_crimes.json", build_sexual_crimes())
    write("hate_crimes.json", build_hate_crimes())
    write("cohort_tenure.json", build_cohort_tenure())
    print("Done.")


if __name__ == "__main__":
    main()
