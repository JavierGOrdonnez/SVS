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
    reports = read_json("data/raw/hate_crimes_mir_2014-2016_2017-2021_2023-2025.json")["reports"]
    reports.sort(key=lambda r: r["year"])
    years = [r["year"] for r in reports]

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

    # Test A — whole-group rate ratio vs pre-2022 baseline. B42 added two more
    # baseline options (pre_2019_only, pre_2020_pooled_2017_2019) to the same
    # CSV -- filtered to the original baseline here so the dashboard keeps
    # exactly one row per test_period (co-rateratio's `periods` array assumes
    # that); the fuller comparison lives in the CSV/reports for anyone who
    # wants it, not (yet) surfaced in this panel.
    DASHBOARD_BASELINE = "pre_2022_pooled_2019_2021"
    period = [r for r in read_csv("data/processed/cohort_tenure_period_test.csv")
              if r["baseline"] == DASHBOARD_BASELINE]
    test_a = defaultdict(lambda: {"periods": [], "rate_ratio": [], "p_value": [], "call": []})
    for r in period:
        g = test_a[r["group"]]
        g["periods"].append(r["test_period"])
        g["rate_ratio"].append(num(r["rate_ratio"]))
        g["p_value"].append(num(r["p_value"]))
        g["call"].append(call(r))

    # Test C — share of all identified perpetrators vs baseline (same filter).
    share = [r for r in read_csv("data/processed/cohort_share_test.csv")
             if r["baseline"] == DASHBOARD_BASELINE]
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


def build_victim_vulnerability():
    """T81: victim-side mirror of peligrosity (V15) -- sexual-crime victims
    per 100k population of the same nationality, not a %-share. Reads
    compute_victim_vulnerability_rates.py's output, grouped by nationality
    the same way build_cohort_tenure() groups by group name above."""
    rows = read_csv("data/processed/victim_vulnerability_rates.csv")

    by_nat = defaultdict(lambda: {
        "iso2": None, "years": [], "victim_count": [], "female_stock": [], "total_stock": [],
        "rate_per_100k_female": [], "rate_per_100k_total": [], "ci_low": [], "ci_high": [],
    })
    for r in rows:
        g = by_nat[r["country_name"]]
        g["iso2"] = r["nationality"]
        g["years"].append(num(r["year"]))
        g["victim_count"].append(num(r["victim_count"]))
        g["female_stock"].append(num(r["female_stock"]))
        g["total_stock"].append(num(r["total_stock"]))
        g["rate_per_100k_female"].append(num(r["rate_per_100k_female"]))
        g["rate_per_100k_total"].append(num(r["rate_per_100k_total"]))
        g["ci_low"].append(num(r["ci_low"]))
        g["ci_high"].append(num(r["ci_high"]))

    return {
        "source": "MIR Informe sobre delitos contra la libertad sexual (victim nationality, T26) + Eurostat migr_pop1ctz via migration_spain.csv (T66 population denominator)",
        "confidence": "medium",
        "caveat": "victim_count is all reported victims of that nationality (both sexes), not a female-only numerator. rate_per_100k_female divides by female-only stock (V6: victims are predominantly but not exclusively female, so this likely overstates the true female-specific rate slightly); rate_per_100k_total divides by that nationality's total stock (both sexes) instead -- shown side by side, neither is the sole framing. 2020 excluded (B38, source-PDF defect in that year's victim-nationality table). ci_low/ci_high (on rate_per_100k_female) capture Poisson count variance only, not population-denominator uncertainty.",
        "nationalities": dict(by_nat),
    }


def build_regularization_sensitivity():
    """T85: upper-bound denominator sensitivity scenario -- assumes the
    ENTIRE 2026 regularization-application pool for a nationality was
    already present throughout 2019-2024, 100% aged 15-59, split male/
    female per that nationality's real registered sex ratio. Original vs.
    over-corrected rate_per_100k, by country and year."""
    rows = read_csv("data/processed/regularization_sensitivity_test.csv")

    by_country = defaultdict(lambda: {
        "years": [], "original_rate_per_100k": [], "over_corrected_rate_per_100k": [],
        "denom_pct_increase": [], "rate_pct_reduction": [],
    })
    for r in rows:
        g = by_country[r["country"].title()]
        g["years"].append(num(r["year"]))
        g["original_rate_per_100k"].append(num(r["original_rate_per_100k"]))
        g["over_corrected_rate_per_100k"].append(num(r["over_corrected_rate_per_100k"]))
        g["denom_pct_increase"].append(num(r["denom_pct_increase"]))
        g["rate_pct_reduction"].append(num(r["rate_pct_reduction"]))

    return {
        "source": "data/raw/regularization_2026.csv (application share by nationality) + migration_spain.csv (registered stock) + sexual_crimes_mir_2017-2024.json (perpetrator counts)",
        "confidence": "medium",
        "caveat": "Explicit UPPER BOUND, not a best estimate: assumes 100% of that nationality's 2026 regularization applicants were already resident in every year 2019-2024, all aged 15-59. Real correction is smaller since not all applicants arrived that early nor are all working-age. Added population is held constant across years (no data on arrival timing); male/female split borrowed from that nationality's own 2024 registered sex ratio. See reports/algeria_morocco_divergence.md for full discussion.",
        "countries": dict(by_country),
    }


def build_general_crime():
    """T84: general (non-nationality-specific) long-run crime trend --
    homicide, robbery, sexual_assault, Spanish vs. foreign only (no
    per-country breakdown exists in this source, see T83's own finding).
    Extends this dashboard's crime coverage back to 2015 using MIR Anuario's
    general "Seguridad Ciudadana" chapter tables (`parse_anuario_general_
    crime.py`), independent of the sexual-crimes-specific Informe/Anuario
    series used elsewhere."""
    rows = read_csv("data/processed/general_crime_trends.csv")
    categories = sorted({r["category"] for r in rows})

    # Per-capita (reported crimes, ALL nationalities -- no split available):
    # indexed to each category's own first available year = 100, since raw
    # rates differ by orders of magnitude across categories (robbery
    # ~150-200/100k vs homicide ~2/100k) and wouldn't share a readable axis
    # otherwise. Raw rate is kept alongside (V14: pair the relative index
    # with its absolute rate), not shown only as an index.
    per_capita = {}
    for cat in categories:
        sub = sorted((r for r in rows if r["category"] == cat and r["metric"] == "per_capita"),
                     key=lambda r: num(r["year"]))
        if not sub:
            continue
        base_rate = num(sub[0]["rate_per_100k"])
        per_capita[cat] = {
            "years": [num(r["year"]) for r in sub],
            "rate_per_100k": [num(r["rate_per_100k"]) for r in sub],
            "index_base100": [round(num(r["rate_per_100k"]) / base_rate * 100, 1) for r in sub],
            "base_year": num(sub[0]["year"]),
        }

    # Spanish vs. foreign detenciones/investigados rate + their ratio, per
    # category. Mirrors this dashboard's peligrosity convention (identified-
    # perpetrator rate, not reported-crime rate) elsewhere -- NOT directly
    # comparable to per_capita above (different numerator: detenciones has
    # a <100% clearance rate against hechos_conocidos).
    foreign_spanish_ratio = {}
    for cat in categories:
        sp = {num(r["year"]): num(r["rate_per_100k"]) for r in rows
              if r["category"] == cat and r["metric"] == "spanish"}
        fo = {num(r["year"]): num(r["rate_per_100k"]) for r in rows
              if r["category"] == cat and r["metric"] == "foreign"}
        years = sorted(set(sp) & set(fo))
        foreign_spanish_ratio[cat] = {
            "years": years,
            "spanish_rate_per_100k": [sp[y] for y in years],
            "foreign_rate_per_100k": [fo[y] for y in years],
            "ratio_foreign_over_spanish": [round(fo[y] / sp[y], 2) if sp[y] else None for y in years],
        }

    return {
        "source": ("MIR Anuario Estadistico 2016-2023, 'Seguridad Ciudadana' chapter general infraction "
                    "tables (not the sexual-crimes-specific Informe/Anuario series used elsewhere) + "
                    "population_spain_midyear_5yr.csv + migration_spain.csv"),
        "confidence": "medium",
        "caveat": ("Spanish-vs-foreign only -- no per-country breakdown exists in this source (T83 checked "
                   "directly). 'per_capita' = reported crimes (hechos conocidos), all nationalities. "
                   "'spanish'/'foreign' = detenciones/investigados (identified perpetrators, matching this "
                   "dashboard's peligrosity convention elsewhere) -- NOT directly comparable to per_capita "
                   "(clearance rate is well under 100%). 'spanish' rate is derived (total - foreign), not a "
                   "source-reported figure. sexual_assault's post-2022 values reflect the LO 10/2022 legal "
                   "reform, same definition-break caveat as the rest of this dashboard."),
        "categories": categories,
        "per_capita": per_capita,
        "foreign_spanish_ratio": foreign_spanish_ratio,
    }
