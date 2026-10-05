#!/usr/bin/env python3
"""
T38 -- hate-crime correlation series: migration rates (T11) × xenophobic
party vote share, 2014-2025.

Correlates the MIR hate-crime series (`racismo_xenofobia` + `total_delitos`,
data/raw/hate_crimes_mir_2014-2025.json) against:
  (a) migration stock (stock_foreign_nationality) and flow
      (flow_immigration_from_abroad), both national totals from T11's
      `migration_spain.csv`;
  (b) Vox's vote share at each general election (2015, 2016, 2019 [using
      the November result -- the one that determined that year's actual
      Congress], 2023) and each European Parliament election (2014, 2019,
      2024) held in Spain -- hardcoded, sourced, confidence=medium (C16:
      agent ⊥ ever set confidence=high).

ONE INPUT DELIBERATELY NOT INCLUDED: the task's third requested series,
CIS "principales problemas" public-worry polling, has no reliable annual
series available. CIS publishes this monthly with large non-seasonal
swings (16.9% Jul-2024 -> 30.4% Sep-2024 -> ~4% by Jul-2025, per Newtral/
maldita.es reporting on the CIS barometer) and no primary 2014-2025 annual
extraction exists in this repo. Acquiring that series (CIS "principales
problemas del país" barometer, 1st-4th place rankings, 2000-2025) is
exactly SPEC.md task N2, still status `.` (not started). Forcing a thin,
unevenly-spaced set of sourced snapshots into this script's Pearson-r
calculation would fall below the n<3 threshold this repo's own
`pearson_r()` convention already rejects, and interpolating the gaps
would manufacture data (C9/C15; see also SPEC.md B40's caution about
unverified synthesized figures). So: documented here as reference-only
context (see CIS_CONCERN_CONTEXT_REFERENCE + the printed caveats), not
fed into any correlation. T38 is marked `~` (partial) in SPEC-crime.md,
not `x`, for exactly this reason -- the CIS leg stays blocked on N2.

All correlations here are descriptive Pearson r on n=3-12 annual/electoral
points, not statistical tests, and are associative only -- not causal
(V18, C8).

Data sources:
  data/raw/hate_crimes_mir_2014-2025.json   (racismo_xenofobia, total_delitos)
  data/raw/migration_spain.csv              (T11: stock_foreign_nationality,
                                              flow_immigration_from_abroad)
  Vox vote shares: es.wikipedia.org "Anexo:Resultados electorales de Vox"
                   (confidence=medium; cross-checked against the party's
                   own es.wikipedia.org article and eleconomista.es/
                   legrandcontinent.eu reporting on the 2024 EP result --
                   all consistent to within rounding)

Output: data/processed/hate_crime_correlates.csv + 1 chart.
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
HATE_CRIME_JSON = ROOT / "data" / "raw" / "hate_crimes_mir_2014-2025.json"
MIGRATION_CSV = ROOT / "data" / "raw" / "migration_spain.csv"
OUT_CSV = ROOT / "data" / "processed" / "hate_crime_correlates.csv"
OUT_CHART = ROOT / "data" / "processed" / "hate_crime_correlates.png"

# Source: es.wikipedia.org "Anexo:Resultados electorales de Vox" (confidence=medium, C16).
# 2019 had two general elections; the November result is the one that
# determined that year's actual Congress and is used here (no attempt to
# average/blend the two into a single "2019" point).
VOX_GENERAL_ELECTION_PCT = {
    2015: 0.23,
    2016: 0.20,
    2019: 15.08,
    2023: 12.38,
}
VOX_EP_ELECTION_PCT = {
    2014: 1.57,
    2019: 6.21,
    2024: 9.63,
}

# Reference only -- NOT fed into any correlation below (see module docstring).
# CIS "principales problemas del país" barometer, % citing immigration among
# the top problems, isolated snapshots (sourced, not an annual series):
#   Jul-2024: 16.9% (4th place) | Sep-2024: 30.4% (1st place, highest since
#   Jul-2007) | Jul-2025: ~4% (8th place). Source: Newtral 2024-09-18
#   ("La inmigración es el principal problema del país..."), corroborated by
#   maldita.es 2024-09-20. The swing size within a single quarter is itself
#   the reason this isn't treated as a usable annual point -- acquiring the
#   real multi-year series is SPEC.md task N2.
CIS_CONCERN_CONTEXT_REFERENCE = {
    "2024-07": 16.9,
    "2024-09": 30.4,
    "2025-07": 4.0,
}


def load_hate_crime_series():
    with open(HATE_CRIME_JSON, encoding="utf-8") as f:
        reports = json.load(f)["reports"]
    racismo_xenofobia, total_delitos = {}, {}
    for rep in reports:
        year = rep["year"]
        cats = {c["category"]: c["count"] for c in rep["categories"]}
        if cats.get("racismo_xenofobia") is not None:
            racismo_xenofobia[year] = cats["racismo_xenofobia"]
        if cats.get("total_delitos") is not None:
            total_delitos[year] = cats["total_delitos"]
    return racismo_xenofobia, total_delitos


def load_migration_totals():
    """National-level annual totals: stock_foreign_nationality, flow_immigration_from_abroad."""
    stock, flow = {}, {}
    with open(MIGRATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["region"] != "national" or r["country_of_origin"] != "all":
                continue
            if r["series"] == "stock_foreign_nationality" and r["sex"] == "all" and r["age_group"] == "all":
                stock[int(r["year"])] = float(r["value"])
            elif (
                r["series"] == "flow_immigration_from_abroad"
                and r["sex"] == "all"
                and r["age_group"] == "all"
                and r["nationality"] == "all"
            ):
                flow[int(r["year"])] = float(r["value"])
    return stock, flow


def pearson_r(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return cov / (sx * sy)


def correlate(series_a, series_b):
    """Return (r, years_used) over the years both series share, or (None, [])."""
    years = sorted(set(series_a) & set(series_b))
    if len(years) < 3:
        return None, years
    xs = [series_a[y] for y in years]
    ys = [series_b[y] for y in years]
    return pearson_r(xs, ys), years


def main():
    racismo_xenofobia, total_delitos = load_hate_crime_series()
    stock, flow = load_migration_totals()

    correlations = {
        "racismo_xenofobia_vs_stock_foreign_nationality": correlate(racismo_xenofobia, stock),
        "racismo_xenofobia_vs_flow_immigration_from_abroad": correlate(racismo_xenofobia, flow),
        "total_delitos_vs_stock_foreign_nationality": correlate(total_delitos, stock),
        "total_delitos_vs_flow_immigration_from_abroad": correlate(total_delitos, flow),
        "racismo_xenofobia_vs_vox_general_election_pct": correlate(racismo_xenofobia, VOX_GENERAL_ELECTION_PCT),
        "racismo_xenofobia_vs_vox_ep_election_pct": correlate(racismo_xenofobia, VOX_EP_ELECTION_PCT),
    }

    rows = []
    for y, v in sorted(racismo_xenofobia.items()):
        rows.append({"section": "hate_crime", "series": "racismo_xenofobia", "year": y, "value": v})
    for y, v in sorted(total_delitos.items()):
        rows.append({"section": "hate_crime", "series": "total_delitos", "year": y, "value": v})
    for y, v in sorted(stock.items()):
        rows.append({"section": "migration", "series": "stock_foreign_nationality", "year": y, "value": v})
    for y, v in sorted(flow.items()):
        rows.append({"section": "migration", "series": "flow_immigration_from_abroad", "year": y, "value": v})
    for y, v in sorted(VOX_GENERAL_ELECTION_PCT.items()):
        rows.append({"section": "vox_vote_share_pct", "series": "general_election", "year": y, "value": v})
    for y, v in sorted(VOX_EP_ELECTION_PCT.items()):
        rows.append({"section": "vox_vote_share_pct", "series": "ep_election", "year": y, "value": v})
    for name, (r, years) in correlations.items():
        rows.append({"section": "correlation", "series": f"{name}_r_n{len(years)}", "year": "", "value": r})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["section", "series", "year", "value"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")

    print()
    print("## Correlations (descriptive only, n=3-12 points -- not statistical tests; V18/C8: associative, not causal)\n")
    for name, (r, years) in correlations.items():
        print(f"  {name}: r={r} (years={years})")

    print()
    print("## Critical Caveats\n")
    print("""  1. CIS PUBLIC-WORRY LEG NOT INCLUDED: this task also asked for public
     polling (CIS "principales problemas" immigration-worry series). No
     reliable annual 2014-2025 series exists in this repo or was found
     during this task; the available sourced snapshots swing too sharply
     within a single year (16.9% Jul-2024 -> 30.4% Sep-2024 -> ~4% Jul-2025)
     to stand in for an annual point without misrepresenting the series.
     Acquiring that series is SPEC.md task N2 (status `.`, not started);
     this script does not block on it but does not fabricate it either.
     Reference snapshots are kept in CIS_CONCERN_CONTEXT_REFERENCE above,
     clearly excluded from every correlate() call.

  2. ASSOCIATIVE ONLY, NOT CAUSAL (V18, C8): a positive or negative Pearson
     r between hate-crime counts and migration stock/flow or Vox vote share
     says nothing about mechanism or direction -- all three series could
     share a common driver (e.g. the same period's immigration salience in
     political discourse), or reporting propensity for hate crimes could
     itself be changing independently of real incidence (see SPEC.md T109's
     documented 2024 reporting-suppression hypothesis, which this script
     does not adjust for).

  3. LOW N FOR ELECTION SERIES: the Vox general-election correlation uses
     only 4 points (2015, 2016, 2019, 2023) and the EP-election correlation
     only 3 (2014, 2019, 2024) -- elections are not annual, so these are
     the only real data points available, not a sampling choice. Treat
     both r values as illustrative, not reliable.

  4. 2019 COLLAPSED TO ONE ELECTION: 2019 had two general elections (April:
     10.26%, November: 15.08%). Only November's result is used here (the
     one that produced that year's actual Congress); April's result is
     documented in the module docstring but not separately correlated.

  5. HATE-CRIME SERIES IS POLICE-RECORDED, NOT VICTIMIZATION: racismo_
     xenofobia/total_delitos reflect reported-and-registered incidents
     (MIR Informe de la Evolución de los Delitos de Odio), not a
     victimization survey -- reporting-rate changes over time are not
     separated from true-incidence changes (same caveat as T109/T110).
""")

    make_chart(racismo_xenofobia, stock, flow)


def make_chart(racismo_xenofobia, stock, flow):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    def scatter(ax, series_b, xlabel):
        years = sorted(set(racismo_xenofobia) & set(series_b))
        xs = [series_b[y] for y in years]
        ys = [racismo_xenofobia[y] for y in years]
        ax.scatter(xs, ys)
        for y in years:
            ax.annotate(str(y), (series_b[y], racismo_xenofobia[y]), fontsize=8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("racismo_xenofobia hate crimes/yr")

    scatter(axes[0, 0], stock, "foreign-resident stock (persons)")
    axes[0, 0].set_title("vs. migration stock")
    scatter(axes[0, 1], flow, "annual immigration inflow (persons)")
    axes[0, 1].set_title("vs. migration flow")
    scatter(axes[1, 0], VOX_GENERAL_ELECTION_PCT, "Vox general-election vote share (%)")
    axes[1, 0].set_title("vs. Vox general election (n=4)")
    scatter(axes[1, 1], VOX_EP_ELECTION_PCT, "Vox EP-election vote share (%)")
    axes[1, 1].set_title("vs. Vox EP election (n=3)")

    fig.suptitle("Hate crimes (racismo_xenofobia) vs. migration & Vox vote share\nDescriptive association only (V18/C8) -- CIS polling leg not included, see caveats")
    fig.tight_layout()
    fig.savefig(OUT_CHART, dpi=150)
    plt.close(fig)
    print(f"Wrote chart -> {OUT_CHART}")


if __name__ == "__main__":
    main()
