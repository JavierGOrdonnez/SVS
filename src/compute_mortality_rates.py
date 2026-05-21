"""Join INE mortality deaths × mid-year population to produce annual rates.

Inputs:
  data/processed/mortality_spain_ine_ecm.csv          — deaths (year × sex × age × cause)
  data/processed/population_spain_midyear_5yr.csv     — July-1 pop (year × sex × age)

Outputs:
  data/processed/mortality_rates.csv         — rate per 100,000 for every cause
  data/processed/mortality_rates_key.csv     — same, filtered to key causes for charts
  data/processed/mortality_rates_all_cause_by_age.csv — concise all-cause rates pivot

Rate definition: rate = deaths / mid_year_population × 100_000

The "all" age group covers Todas las edades; "all" sex covers Ambos sexos.
For these we use the corresponding total population row.
"""

import csv
import sys
from collections import defaultdict

KEY_CAUSES = {
    "Todas las causas",
    "Agresiones (homicidio)",
    "Suicidio y lesiones autoinfligidas",
    "Accidentes de tráfico",
    "Trastornos mentales debidos al uso de drogas (drogodependencia, toxicomanía)",
    "Envenenamiento accidental por psicofármacos y drogas de abuso",
    "Eventos de intención no determinada",
}


def main(mort_path: str, pop_path: str) -> int:
    # pop[(year, sex, age_group)] = population
    pop: dict = {}
    with open(pop_path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            pop[(int(row["year"]), row["sex"], row["age_group"])] = int(row["population_july1"])

    # All-age totals from pop (for joining all-age mortality rows)
    pop_all_age: dict = defaultdict(int)  # (year, sex) -> pop
    for (y, s, a), v in pop.items():
        pop_all_age[(y, s)] += v
    for (y, s), v in pop_all_age.items():
        pop[(y, s, "all")] = v

    out_full = "data/processed/mortality_rates.csv"
    out_key = "data/processed/mortality_rates_key.csv"
    out_all_cause = "data/processed/mortality_rates_all_cause_by_age.csv"

    full_rows = []
    key_rows = []
    all_cause_rows = []

    skipped_no_pop = 0
    with open(mort_path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            year = int(row["year"])
            sex = row["sex"]
            age = row["age_group"]
            deaths = int(row["deaths"])
            cause = row["cause"]
            chapter = row["cause_chapter"]

            denom = pop.get((year, sex, age))
            if denom is None or denom == 0:
                skipped_no_pop += 1
                continue
            rate = deaths / denom * 100_000.0

            out = {
                "year": year,
                "sex": sex,
                "age_group": age,
                "cause_chapter": chapter,
                "cause": cause,
                "deaths": deaths,
                "population": denom,
                "rate_per_100k": round(rate, 4),
            }
            full_rows.append(out)
            if cause in KEY_CAUSES:
                key_rows.append(out)
            if cause == "Todas las causas" and chapter == "I-XXII":
                all_cause_rows.append(out)

    full_rows.sort(key=lambda r: (r["year"], r["sex"], r["age_group"], r["cause_chapter"], r["cause"]))
    key_rows.sort(key=lambda r: (r["year"], r["sex"], r["age_group"], r["cause"]))
    all_cause_rows.sort(key=lambda r: (r["year"], r["sex"], r["age_group"]))

    cols = ["year", "sex", "age_group", "cause_chapter", "cause", "deaths", "population", "rate_per_100k"]
    for path, rows in [(out_full, full_rows), (out_key, key_rows), (out_all_cause, all_cause_rows)]:
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        print(f"{path}: {len(rows)} rows")

    print(f"skipped (no matching population row): {skipped_no_pop}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
