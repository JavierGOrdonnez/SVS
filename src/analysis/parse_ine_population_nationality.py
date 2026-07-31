"""Parse INE table 56936 (Población residente por fecha, sexo, grupo de edad y
nacionalidad) into a tidy CSV — the direct, source-reported Spanish/foreign
nationality population split.

Source: https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/56936.csv?nocab=1

Fixes B44 (SPEC.md): every prior consumer of "Spanish-national population"
in this repo derived it as `total_population(INE t.56934) - foreign_stock
(Eurostat migr_pop1ctz)`, mixing a July-1 total with a January-1 foreign
figure covering only the top ~50 nationalities (~86-94% of foreign
residents). Table 56936 is the same ECP product family as t.56934 (same
quarterly cadence, same July-1 midyear reference date) but reports the
"Española" nationality directly — no subtraction needed.

Output:
  data/processed/population_spain_nationality.csv — July 1, 2002-2025,
  year x sex x age_group x nationality -> population. age_group is either
  "all" (INE's own "Todas las edades" row) or one of the 17 pyramid bands
  (0-4, 5-9, ..., 75-79, 80+) already used by
  src/migration/build_dashboard_data.py's PYRAMID_AGES; the raw source's
  De 80 a 84/De 85 a 89/90 y más años bands are summed into 80+.

Per V46: this series starts 2002 (table 56936's real floor) — do not
back-fill earlier years via the old subtraction method.
"""

import csv
import re
import sys

SEX_MAP = {
    "Total": "all",
    "Ambos sexos": "all",
    "Hombres": "male",
    "Mujeres": "female",
}

NATIONALITY_MAP = {
    "Española": "spanish",
    "Extranjera": "foreign",
    "Total": "total",
}

PERIOD_MONTH = {
    "enero": "01-01",
    "abril": "04-01",
    "julio": "07-01",
    "octubre": "10-01",
}

AGE_MAP = {
    "Todas las edades": "all",
    "De 0 a 4 años": "0-4",
    "De 5 a 9 años": "5-9",
    "De 10 a 14 años": "10-14",
    "De 15 a 19 años": "15-19",
    "De 20 a 24 años": "20-24",
    "De 25 a 29 años": "25-29",
    "De 30 a 34 años": "30-34",
    "De 35 a 39 años": "35-39",
    "De 40 a 44 años": "40-44",
    "De 45 a 49 años": "45-49",
    "De 50 a 54 años": "50-54",
    "De 55 a 59 años": "55-59",
    "De 60 a 64 años": "60-64",
    "De 65 a 69 años": "65-69",
    "De 70 a 74 años": "70-74",
    "De 75 a 79 años": "75-79",
    "De 80 a 84 años": "80+",
    "De 85 a 89 años": "80+",
    "90 y más años": "80+",
}

MIN_YEAR = 2002  # V46: table 56936's real floor -- do not back-fill earlier.


def parse_value(s: str):
    """Return int, or None if value is missing/suppressed."""
    s = s.strip().strip('"')
    if not s or s in ("..", "."):
        return None
    if "," in s:
        s = s.split(",", 1)[0]
    s = s.replace(".", "")
    return int(s)


def parse_periodo(p: str):
    m = re.match(r"(\d+) de (\w+) de (\d{4})", p.strip())
    if not m:
        return None
    day, month, year = m.group(1), m.group(2).lower(), int(m.group(3))
    if month not in PERIOD_MONTH:
        return None
    return year, PERIOD_MONTH[month]


def main(in_path: str, out_path: str = "data/processed/population_spain_nationality.csv") -> int:
    # (year, sex, age_group, nationality) -> population, July 1 only
    totals: dict = {}

    with open(in_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        for row in reader:
            if len(row) < 5:
                continue
            nationality_raw, age_raw, sex_raw, periodo, value_raw = row[0], row[1], row[2], row[3], row[4]

            nationality = NATIONALITY_MAP.get(nationality_raw.strip())
            if nationality is None:
                continue  # individual country/region row -- not needed here

            sex = SEX_MAP.get(sex_raw)
            if sex is None:
                continue

            age_group = AGE_MAP.get(age_raw.strip())
            if age_group is None:
                continue

            pp = parse_periodo(periodo)
            if pp is None:
                continue
            year, month_day = pp
            if month_day != "07-01" or year < MIN_YEAR:
                continue

            value = parse_value(value_raw)
            if value is None:
                continue

            key = (year, sex, age_group, nationality)
            totals[key] = totals.get(key, 0) + value

    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "sex", "age_group", "nationality", "population_july1"])
        for (year, sex, age_group, nationality), value in sorted(totals.items()):
            w.writerow([year, sex, age_group, nationality, value])
    print(f"{out_path}: {len(totals)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
