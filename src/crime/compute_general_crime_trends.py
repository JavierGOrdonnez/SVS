#!/usr/bin/env python3
"""
T83 -- turns `data/raw/mir_anuario_general_crime_2015-2023.csv` (T82-style
extraction from MIR Anuario's general "Seguridad Ciudadana" chapter, 3
categories: homicide, robbery, sexual_assault) into rates:

  (a) per-capita trend: hechos_conocidos_total (ALL nationalities, no split
      available in this source) / total Spain population * 100k.
  (b) Spanish-vs-foreign detention/investigation rate: detenciones_total
      minus detenciones_foreign (='spanish', derived -- not a source-
      reported figure) and detenciones_foreign directly, each divided by
      its own population (Spanish = total - foreign stock; foreign = total
      foreign stock) * 100k. Mirrors this repo's existing peligrosity
      convention (V15: [convicted, identified] bracket, arrests/investigated
      as numerator) rather than hechos_conocidos (reported crimes, which
      has no nationality split in this source at all).

Denominators: data/processed/population_spain_midyear_5yr.csv (total, all
years summed across age bands, sex='all') and data/raw/migration_spain.csv
stock_foreign_nationality/country_of_origin=all/nationality=foreign/sex=all/
age_group=all (foreign stock total) -- both already continuous well beyond
this task's 2015-2023 window (population back to 1971, foreign stock to
2000), so no coverage gaps here.

Confidence: 'medium' throughout (a real MIR count over a real population
denominator, not a directly-published rate) -- never 'high' (C16).

Output: data/processed/general_crime_trends.csv
  columns: year, category, metric, rate_per_100k, count, population, confidence, notes
  metric in {per_capita, spanish, foreign}
"""
import csv
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
RAW_CSV = ROOT / "data" / "raw" / "mir_anuario_general_crime_2015-2023.csv"
POP_CSV = ROOT / "data" / "processed" / "population_spain_midyear_5yr.csv"
MIGRATION_CSV = ROOT / "data" / "raw" / "migration_spain.csv"
OUT_CSV = ROOT / "data" / "processed" / "general_crime_trends.csv"

CATEGORIES = ["homicide", "robbery", "sexual_assault"]


def load_total_population() -> dict[int, float]:
    pop = {}
    with open(POP_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["sex"] != "all":
                continue
            y = int(r["year"])
            pop[y] = pop.get(y, 0.0) + float(r["population_july1"])
    return pop


def load_foreign_stock() -> dict[int, float]:
    stock = {}
    with open(MIGRATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["series"] == "stock_foreign_nationality" and r["country_of_origin"] == "all"
                    and r["nationality"] == "foreign" and r["sex"] == "all" and r["age_group"] == "all"):
                stock[int(r["year"])] = float(r["value"])
    return stock


def load_raw() -> list[dict]:
    with open(RAW_CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_rows():
    raw = load_raw()
    total_pop = load_total_population()
    foreign_pop = load_foreign_stock()

    conocidos = {}   # (year, category) -> count
    detenciones = {}  # (year, category) -> count
    foreign = {}      # (year, category) -> count (sex='all' only)
    for r in raw:
        y, cat, metric, sex, count = int(r["year"]), r["category"], r["metric"], r["sex"], int(r["count"])
        if metric == "hechos_conocidos_total" and sex == "all":
            conocidos[(y, cat)] = count
        elif metric == "detenciones_total" and sex == "all":
            detenciones[(y, cat)] = count
        elif metric == "detenciones_foreign" and sex == "all":
            foreign[(y, cat)] = count

    rows = []

    # (a) per-capita, all nationalities, hechos conocidos (reported crimes)
    for (y, cat), count in sorted(conocidos.items()):
        pop = total_pop.get(y)
        if pop is None:
            continue
        rows.append({
            "year": y, "category": cat, "metric": "per_capita",
            "rate_per_100k": round(count / pop * 100_000, 2),
            "count": count, "population": round(pop), "confidence": "medium",
            "notes": ("hechos conocidos (crimes reported to police), ALL nationalities -- this MIR Anuario "
                      "source has no nationality split for reported crimes, only for detenciones/investigados "
                      "(see 'spanish'/'foreign' metric rows). Not directly comparable to the sexual-crimes "
                      "Informe/Anuario series' own totals across the LO 10/2022 reform boundary (2022+) -- "
                      "same definition-break caveat as elsewhere in this dashboard."),
        })

    # (b) Spanish vs. foreign, detenciones e investigados (identified perpetrators)
    for (y, cat), total in sorted(detenciones.items()):
        for_count = foreign.get((y, cat))
        if for_count is None:
            continue
        sp_count = total - for_count
        sp_pop = total_pop.get(y)
        for_pop = foreign_pop.get(y)
        if sp_pop is not None and for_pop is not None:
            sp_pop_adj = sp_pop - for_pop  # Spanish-only population = total - foreign stock
            rows.append({
                "year": y, "category": cat, "metric": "spanish",
                "rate_per_100k": round(sp_count / sp_pop_adj * 100_000, 2),
                "count": sp_count, "population": round(sp_pop_adj), "confidence": "medium",
                "notes": ("detenciones/investigados attributed to Spanish nationals, DERIVED as "
                          "detenciones_total - detenciones_foreign (not a source-reported figure). "
                          "Denominator = total population - foreign stock."),
            })
            rows.append({
                "year": y, "category": cat, "metric": "foreign",
                "rate_per_100k": round(for_count / for_pop * 100_000, 2),
                "count": for_count, "population": round(for_pop), "confidence": "medium",
                "notes": ("detenciones/investigados attributed to foreign nationals (source-reported, "
                          "not per-country -- see reg-sensitivity/cohort-tenure panels for Morocco/Algeria-"
                          "specific rates). Denominator = total foreign stock (Eurostat migr_pop1ctz)."),
            })

    rows.sort(key=lambda r: (r["category"], r["metric"], r["year"]))
    return rows


def main():
    rows = build_rows()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year", "category", "metric", "rate_per_100k", "count",
                                          "population", "confidence", "notes"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")

    for cat in CATEGORIES:
        for metric in ("per_capita", "spanish", "foreign"):
            sub = [r for r in rows if r["category"] == cat and r["metric"] == metric]
            years = [r["year"] for r in sub]
            print(f"  {cat:15} {metric:10} years {years}")


if __name__ == "__main__":
    main()
