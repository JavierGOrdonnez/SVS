"""Emit JS constants for the mortality tab of docs/index.html.

Reads the processed CSVs and writes a self-contained JS block to stdout
that the dashboard can paste/include verbatim. Keeps the dashboard a
single static file (no fetch / CORS / build step).
"""

import csv
import json
import sys
from collections import defaultdict

KEY_CAUSES_DISPLAY = {
    "Todas las causas": "All causes",
    "Agresiones (homicidio)": "Homicide",
    "Suicidio y lesiones autoinfligidas": "Suicide",
    "Accidentes de tráfico": "Traffic accident",
    "Trastornos mentales debidos al uso de drogas (drogodependencia, toxicomanía)": "Drug-use disorders",
    "Envenenamiento accidental por psicofármacos y drogas de abuso": "Accidental drug poisoning",
    "Eventos de intención no determinada": "Undetermined intent",
}

REPRO_AGES = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44"]
YOUNG_AGE = "20-24"


def load_rates_key(path):
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            out.append(
                {
                    "year": int(r["year"]),
                    "sex": r["sex"],
                    "age_group": r["age_group"],
                    "cause": r["cause"],
                    "deaths": int(r["deaths"]),
                    "rate": float(r["rate_per_100k"]),
                }
            )
    return out


def load_chapter(path):
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            out.append(
                {
                    "year": int(r["year"]),
                    "sex": r["sex"],
                    "chapter": r["cause_chapter"],
                    "deaths": int(r["deaths"]),
                }
            )
    return out


def build():
    """Return the mortality-tab data blob (also reused by build_dashboard.py)."""
    rates = load_rates_key("data/processed/mortality_rates_key.csv")
    chap = load_chapter("data/processed/mortality_by_chapter.csv")
    all_age = []
    with open("data/processed/mortality_rates.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["age_group"] == "all" and r["cause"] == "Todas las causas":
                all_age.append(
                    {
                        "year": int(r["year"]),
                        "sex": r["sex"],
                        "rate": float(r["rate_per_100k"]),
                        "deaths": int(r["deaths"]),
                    }
                )

    years = sorted({r["year"] for r in all_age})

    # 1. All-cause rate per 100k, by sex, all ages, 2000–2024
    s1 = {"years": years}
    for sex in ("male", "female"):
        s1[sex] = [
            next((r["rate"] for r in all_age if r["year"] == y and r["sex"] == sex), None)
            for y in years
        ]

    # 2. Female deaths by chapter over time (counts, top 7)
    fem_chap = [r for r in chap if r["sex"] == "female"]
    chap_totals = defaultdict(int)
    for r in fem_chap:
        chap_totals[r["chapter"]] += r["deaths"]
    top_chapters = [
        c for c, _ in sorted(chap_totals.items(), key=lambda kv: -kv[1])[:7]
    ]
    s2 = {"years": years, "chapters": top_chapters, "series": {}}
    for c in top_chapters:
        s2["series"][c] = [
            next((r["deaths"] for r in fem_chap if r["year"] == y and r["chapter"] == c), 0)
            for y in years
        ]

    # 3. Female age profile — key external-cause rates per 100k, latest year
    latest = max(years)
    latest_rows = [r for r in rates if r["sex"] == "female" and r["year"] == latest]
    age_order = ["<1", "1-4", "5-9", "10-14"] + [f"{x}-{x+4}" for x in range(15, 95, 5)] + ["95+"]
    s3 = {"year": latest, "ages": age_order, "series": {}}
    for cause, label in KEY_CAUSES_DISPLAY.items():
        if cause == "Todas las causas":
            continue
        s3["series"][label] = [
            next((r["rate"] for r in latest_rows if r["age_group"] == a and r["cause"] == cause), 0.0)
            for a in age_order
        ]

    # 4. Female external-cause rates over time (all ages)
    fem_allage = [r for r in rates if r["sex"] == "female" and r["age_group"] == "all"]
    s4 = {"years": years, "series": {}}
    for cause, label in KEY_CAUSES_DISPLAY.items():
        if cause == "Todas las causas":
            continue
        s4["series"][label] = [
            next((r["rate"] for r in fem_allage if r["year"] == y and r["cause"] == cause), 0.0)
            for y in years
        ]

    # 5. Reproductive-age (15-44) cohort female rates over time, per cause
    fem_repro_year = {}
    for r in rates:
        if r["sex"] != "female" or r["age_group"] not in REPRO_AGES:
            continue
        key = (r["year"], r["cause"])
        fem_repro_year.setdefault(key, {"d": 0})["d"] += r["deaths"]
    # population denominator: read mortality_rates again for these cells where cause = "Todas las causas"
    pop_by_year_age = {}
    with open("data/processed/mortality_rates.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["sex"] == "female" and r["age_group"] in REPRO_AGES and r["cause"] == "Todas las causas":
                pop_by_year_age[(int(r["year"]), r["age_group"])] = int(r["population"])
    pop_repro_year = defaultdict(int)
    for (y, a), p in pop_by_year_age.items():
        pop_repro_year[y] += p

    s5 = {"years": years, "series": {}}
    for cause, label in KEY_CAUSES_DISPLAY.items():
        if cause == "Todas las causas":
            continue
        s5["series"][label] = []
        for y in years:
            d = fem_repro_year.get((y, cause), {"d": 0})["d"]
            p = pop_repro_year.get(y, 0)
            s5["series"][label].append(round(d / p * 100_000, 4) if p else None)

    # 6. Female 20-24 cause profile in latest year — bar of top 12 specific causes by deaths
    fem_2024_2024 = {}
    with open("data/processed/mortality_spain_ine_ecm.csv", newline="") as f:
        for r in csv.DictReader(f):
            if (
                r["sex"] == "female"
                and r["age_group"] == YOUNG_AGE
                and int(r["year"]) == latest
                and r["cause_chapter"] == ""  # specific cause, not chapter total
            ):
                fem_2024_2024[r["cause"]] = int(r["deaths"])
    top_causes = sorted(fem_2024_2024.items(), key=lambda kv: -kv[1])[:12]
    s6 = {
        "year": latest,
        "age": YOUNG_AGE,
        "labels": [c for c, _ in top_causes],
        "deaths": [d for _, d in top_causes],
    }

    return {
        "all_cause_by_sex": s1,
        "female_chapter_over_time": s2,
        "female_age_profile_latest": s3,
        "female_external_over_time": s4,
        "female_repro_over_time": s5,
        "female_young_top_causes": s6,
    }


def main():
    # Legacy CLI: emit as a JS const block on stdout.
    blob = build()
    js = "const MORTALITY = " + json.dumps(blob, ensure_ascii=False, separators=(",", ":")) + ";\n"
    sys.stdout.write(js)


if __name__ == "__main__":
    main()
