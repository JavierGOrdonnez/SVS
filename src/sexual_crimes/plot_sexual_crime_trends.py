#!/usr/bin/env python3
"""
T42 -- sexual-crime evolution (2019-2024) + migration-correlation charts.

(a) Per-category time series, collapsing the LO 10/2022 "abuso"->"agresion"
    legal reclassification per V24 (pre-2022 abuso_sexual + agresion_sexual
    summed into one unified series; same for the con_penetracion pair).
(b) Per-nationality perpetrator time series: Spanish vs. foreign totals
    (reconstructed from T26's region subtotals + the report's foreign_pct,
    since MIR never publishes an absolute Spanish perpetrator count directly)
    plus the per-country series for the 4 nationalities present in every
    report year with matching migration-flow data (Morocco, Algeria,
    Colombia, Romania).
(c) Correlate total sexual-crime counts against: annual migration inflow,
    migrant population share, and 3-yr cumulative inflow by nationality
    (generalizes V25's cohort window beyond Morocco/Algeria to any
    nationality with a flow series in migration_spain.csv).

Only 5 MIR report years exist (2019, 2021-2024, no 2020 report) so every
correlation here is a low-n descriptive Pearson r, not a statistical test --
report association only, no causal claims (V9).

Data sources:
  data/raw/sexual_crimes_mir_2019-2024.json   (T26)
  data/raw/migration_spain.csv                (T11/V25)
  data/processed/population_spain_midyear_5yr.csv

Output: data/processed/sexual_crime_evolution.csv + 3 charts.
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
MIR_JSON = ROOT / "data" / "raw" / "sexual_crimes_mir_2019-2024.json"
MIGRATION_CSV = ROOT / "data" / "raw" / "migration_spain.csv"
POP_CSV = ROOT / "data" / "processed" / "population_spain_midyear_5yr.csv"
OUT_CSV = ROOT / "data" / "processed" / "sexual_crime_evolution.csv"
OUT_CHART_CATEGORY = ROOT / "data" / "processed" / "sexual_crime_category_trends.png"
OUT_CHART_NATIONALITY = ROOT / "data" / "processed" / "sexual_crime_nationality_trends.png"
OUT_CHART_CORRELATION = ROOT / "data" / "processed" / "sexual_crime_migration_correlation.png"

# V24 collapse: pre-2022 category name -> unified name; post-2022 category name -> same unified name
CATEGORY_UNIFY = {
    "abuso_sexual": "agresion_sexual_unified",
    "agresion_sexual": "agresion_sexual_unified",
    "agresion_sexual_post_lo10_2022": "agresion_sexual_unified",
    "abuso_sexual_con_penetracion": "agresion_sexual_con_penetracion_unified",
    "agresion_sexual_con_penetracion": "agresion_sexual_con_penetracion_unified",
    "agresion_sexual_con_penetracion_post_lo10_2022": "agresion_sexual_con_penetracion_unified",
}

# MIR country-name spelling varies by year; normalize to migration_spain.csv's
# country_of_origin ISO2 codes for the countries present in every report year
# AND with a usable flow series in migration_spain.csv.
COUNTRY_NORMALIZE = {
    "MARRUECOS": "MA", "ARGELIA": "DZ", "COLOMBIA": "CO", "RUMANIA": "RO",
}
CORRELATION_COUNTRIES = ["MA", "DZ", "CO", "RO"]
COHORT_WINDOW_YEARS = 3


def load_mir():
    with open(MIR_JSON, encoding="utf-8") as f:
        return json.load(f)["reports"]


def load_migration_totals():
    """Return dict keyed by (country_of_origin, series, nationality) -> {year: value}."""
    totals = {}
    with open(MIGRATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["sex"] != "all" or r["age_group"] != "all":
                continue
            key = (r["country_of_origin"], r["series"], r["nationality"])
            totals.setdefault(key, {})[int(r["year"])] = float(r["value"])
    return totals


def load_population():
    pop = {}
    with open(POP_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["sex"] != "all":
                continue
            y = int(r["year"])
            pop[y] = pop.get(y, 0) + float(r["population_july1"])
    return pop


# ── (a) category trends ─────────────────────────────────────────────────

def build_category_series(reports):
    series = {}  # unified_name -> {year: count}
    for rep in reports:
        year = rep["year"]
        year_totals = {}
        for c in rep["categories"]:
            name = CATEGORY_UNIFY.get(c["category"], c["category"])
            year_totals[name] = year_totals.get(name, 0) + c["count"]
        for name, count in year_totals.items():
            series.setdefault(name, {})[year] = count
    return series


# ── (b) nationality trends ──────────────────────────────────────────────

def build_nationality_series(reports):
    spanish, foreign = {}, {}
    by_country = {code: {} for code in CORRELATION_COUNTRIES}

    for rep in reports:
        year = rep["year"]
        perp = rep["nationality"]["perpetrators"]
        foreign_total = sum(e["total"] for e in perp["by_country"] if e["is_region_total"])
        foreign_pct = perp["foreign_pct"]
        if foreign_pct:
            total_perp = round(foreign_total / (foreign_pct / 100))
            spanish[year] = total_perp - foreign_total
            foreign[year] = foreign_total

        for e in perp["by_country"]:
            if e["is_region_total"]:
                continue
            code = COUNTRY_NORMALIZE.get(e["name"])
            if code in by_country:
                by_country[code][year] = e["total"]

    return spanish, foreign, by_country


# ── (c) migration correlation ───────────────────────────────────────────

def cumulative_inflow(flow_by_year, year, window=COHORT_WINDOW_YEARS):
    years = range(year - window + 1, year + 1)
    vals = [flow_by_year.get(y) for y in years]
    if any(v is None for v in vals):
        return None
    return sum(vals)


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


def main():
    reports = load_mir()
    migration = load_migration_totals()
    population = load_population()

    total_crime_by_year = {rep["year"]: rep["total_count"] for rep in reports}

    category_series = build_category_series(reports)
    spanish_series, foreign_series, country_perp_series = build_nationality_series(reports)

    # national aggregate flow (country_of_origin='all', nationality='all') and
    # total foreign stock (country_of_origin='all', nationality='foreign' --
    # the 'stock_foreign_nationality' series tags the total-foreign row this way)
    inflow_total = migration.get(("all", "flow_immigration_from_abroad", "all"), {})
    stock_total = migration.get(("all", "stock_foreign_nationality", "foreign"), {})
    migrant_share_pct = {
        y: stock_total[y] / population[y] * 100
        for y in stock_total if y in population
    }

    # per-country flow (country_of_origin=code, nationality=code, since T11 rows
    # tag origin-nationality flow rows with nationality==country_of_origin)
    country_flow = {}
    for code in CORRELATION_COUNTRIES:
        country_flow[code] = migration.get((code, "flow_immigration_from_abroad", code), {})

    rows = []
    for name, by_year in category_series.items():
        for y, v in sorted(by_year.items()):
            rows.append({"section": "category", "series": name, "year": y, "value": v})
    for y, v in sorted(spanish_series.items()):
        rows.append({"section": "nationality_total", "series": "spanish", "year": y, "value": v})
    for y, v in sorted(foreign_series.items()):
        rows.append({"section": "nationality_total", "series": "foreign", "year": y, "value": v})
    for code, by_year in country_perp_series.items():
        for y, v in sorted(by_year.items()):
            rows.append({"section": "nationality_country", "series": code, "year": y, "value": v})
    for y, v in sorted(inflow_total.items()):
        rows.append({"section": "migration_inflow_total", "series": "all", "year": y, "value": v})
    for y, v in sorted(migrant_share_pct.items()):
        rows.append({"section": "migrant_pop_share_pct", "series": "all", "year": y, "value": v})
    for code in CORRELATION_COUNTRIES:
        for y in sorted(country_perp_series[code]):
            cum = cumulative_inflow(country_flow[code], y)
            if cum is not None:
                rows.append({"section": "cumulative_inflow_3yr_country", "series": code, "year": y, "value": cum})

    # correlations (descriptive only, n<=5 -- see docstring caveat)
    years_common = sorted(set(total_crime_by_year) & set(inflow_total))
    r_inflow = pearson_r([total_crime_by_year[y] for y in years_common], [inflow_total[y] for y in years_common])
    years_share = sorted(set(total_crime_by_year) & set(migrant_share_pct))
    r_share = pearson_r([total_crime_by_year[y] for y in years_share], [migrant_share_pct[y] for y in years_share])

    r_by_country = {}
    for code in CORRELATION_COUNTRIES:
        yrs = sorted(y for y in country_perp_series[code] if cumulative_inflow(country_flow[code], y) is not None)
        if len(yrs) >= 3:
            xs = [country_perp_series[code][y] for y in yrs]
            ys = [cumulative_inflow(country_flow[code], y) for y in yrs]
            r_by_country[code] = pearson_r(xs, ys)

    rows.append({"section": "correlation", "series": "total_crimes_vs_inflow_total_r", "year": "", "value": r_inflow})
    rows.append({"section": "correlation", "series": "total_crimes_vs_migrant_share_pct_r", "year": "", "value": r_share})
    for code, r in r_by_country.items():
        rows.append({"section": "correlation", "series": f"{code}_crimes_vs_3yr_cumulative_inflow_r", "year": "", "value": r})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["section", "series", "year", "value"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")

    print(f"  total_crimes vs migration_inflow_total: r={r_inflow}")
    print(f"  total_crimes vs migrant_pop_share_pct:   r={r_share}")
    for code, r in r_by_country.items():
        print(f"  {code} crimes vs 3yr-cumulative-inflow:   r={r}")
    print("  CAVEAT: n<=5 report years -- these are descriptive associations only, not tests.")

    make_charts(category_series, spanish_series, foreign_series, country_perp_series,
                total_crime_by_year, inflow_total, migrant_share_pct)


def make_charts(category_series, spanish_series, foreign_series, country_perp_series,
                 total_crime_by_year, inflow_total, migrant_share_pct):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # (a) category trends
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for name, by_year in sorted(category_series.items()):
        years = sorted(by_year)
        ax.plot(years, [by_year[y] for y in years], marker="o", label=name)
    ax.set_title("Sexual-crime categories, 2019-2024 (LO 10/2022 abuso/agresion collapsed per V24)")
    ax.set_xlabel("year")
    ax.set_ylabel("reported count")
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    fig.tight_layout()
    fig.savefig(OUT_CHART_CATEGORY, dpi=150)
    plt.close(fig)

    # (b) nationality trends
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    years_sp = sorted(spanish_series)
    axes[0].plot(years_sp, [spanish_series[y] for y in years_sp], marker="o", label="spanish")
    axes[0].plot(years_sp, [foreign_series[y] for y in years_sp], marker="o", label="foreign")
    axes[0].set_title("Perpetrators: Spanish vs. foreign (reconstructed)")
    axes[0].set_xlabel("year")
    axes[0].legend()

    for code, by_year in country_perp_series.items():
        years = sorted(by_year)
        axes[1].plot(years, [by_year[y] for y in years], marker="o", label=code)
    axes[1].set_title("Perpetrators by nationality (top 4 stable countries)")
    axes[1].set_xlabel("year")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(OUT_CHART_NATIONALITY, dpi=150)
    plt.close(fig)

    # (c) migration correlation
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    years1 = sorted(set(total_crime_by_year) & set(inflow_total))
    axes[0].scatter([inflow_total[y] for y in years1], [total_crime_by_year[y] for y in years1])
    for y in years1:
        axes[0].annotate(str(y), (inflow_total[y], total_crime_by_year[y]), fontsize=8)
    axes[0].set_xlabel("annual migration inflow (all origins)")
    axes[0].set_ylabel("total sexual crimes reported")
    axes[0].set_title("Total crimes vs. annual inflow")

    years2 = sorted(set(total_crime_by_year) & set(migrant_share_pct))
    axes[1].scatter([migrant_share_pct[y] for y in years2], [total_crime_by_year[y] for y in years2])
    for y in years2:
        axes[1].annotate(str(y), (migrant_share_pct[y], total_crime_by_year[y]), fontsize=8)
    axes[1].set_xlabel("migrant population share (%)")
    axes[1].set_ylabel("total sexual crimes reported")
    axes[1].set_title("Total crimes vs. migrant population share")
    fig.suptitle("Descriptive association only (n<=5 report years) -- not a causal test")
    fig.tight_layout()
    fig.savefig(OUT_CHART_CORRELATION, dpi=150)
    plt.close(fig)

    print(f"Wrote charts -> {OUT_CHART_CATEGORY}, {OUT_CHART_NATIONALITY}, {OUT_CHART_CORRELATION}")


if __name__ == "__main__":
    main()
