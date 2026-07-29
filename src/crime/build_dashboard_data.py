"""Build the hate_crimes.json and cohort_tenure.json dashboard data blobs.

Reads the MIR "Delitos de Odio" JSON + the cohort-tenure test CSVs, returns
the dicts written to docs/data/hate_crimes.json and
docs/data/cohort_tenure.json — same shape as before this file was split
out of src/analysis/build_dashboard.py.
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


def build_victim_vulnerability():
    """T80: victim-side mirror of peligrosity (V15) -- sexual-crime victims
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
