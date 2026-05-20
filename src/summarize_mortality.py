"""Build compact mortality summaries from the full INE ECM CSV.

Outputs three derived files:
  data/processed/mortality_by_chapter.csv      — year × sex × chapter (all ages)
  data/processed/mortality_by_age_sex.csv      — year × sex × age (all-cause)
  data/processed/mortality_key_causes.csv      — year × sex × age × cause (curated cause list)

The "key causes" file is filtered to a small set relevant to the SVS project:
violence, suicide, traffic accidents, drug overdose, all-cause — so we can chart
violence deaths alongside competing-risk causes for women.
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


def main(in_path: str) -> int:
    by_chapter = defaultdict(int)  # (year, sex, chapter) -> deaths
    by_age_sex = defaultdict(int)  # (year, sex, age) -> deaths (all-cause only)
    key_rows = []

    with open(in_path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            year = int(row["year"])
            sex = row["sex"]
            age = row["age_group"]
            chapter = row["cause_chapter"]
            cause = row["cause"]
            deaths = int(row["deaths"])

            if age == "all" and chapter and chapter != "I-XXII":
                by_chapter[(year, sex, chapter)] += deaths

            if cause == "Todas las causas" and chapter == "I-XXII":
                by_age_sex[(year, sex, age)] = deaths

            if cause in KEY_CAUSES:
                key_rows.append(
                    {
                        "year": year,
                        "sex": sex,
                        "age_group": age,
                        "cause": cause,
                        "deaths": deaths,
                    }
                )

    out_chapter = "data/processed/mortality_by_chapter.csv"
    with open(out_chapter, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "sex", "cause_chapter", "deaths"])
        for (y, s, c), v in sorted(by_chapter.items()):
            w.writerow([y, s, c, v])
    print(f"{out_chapter}: {len(by_chapter)} rows")

    out_age = "data/processed/mortality_by_age_sex.csv"
    with open(out_age, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "sex", "age_group", "deaths_all_cause"])
        for (y, s, a), v in sorted(by_age_sex.items()):
            w.writerow([y, s, a, v])
    print(f"{out_age}: {len(by_age_sex)} rows")

    out_key = "data/processed/mortality_key_causes.csv"
    key_rows.sort(key=lambda r: (r["year"], r["sex"], r["age_group"], r["cause"]))
    with open(out_key, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "sex", "age_group", "cause", "deaths"])
        w.writeheader()
        w.writerows(key_rows)
    print(f"{out_key}: {len(key_rows)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
