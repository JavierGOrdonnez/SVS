"""Parse INE table 56934 (Estimaciones de la Población Actual de España) into tidy CSVs.

Source: https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/56934.csv?nocab=1

Outputs:
  data/processed/population_spain_estimates.csv   — full long form 1971–2025 quarterly
  data/processed/population_spain_midyear_5yr.csv — July 1 mid-year, 5-yr age groups
                                                    matching INE ECM mortality table
                                                    (used as rate denominator)

Age group mapping (mortality table 7947 bins):
  <1   → "0 años"
  1-4  → "1 año".."4 años"
  5-9  → "5 años".."9 años"
  ...
  90-94 → "90 años".."94 años"
  95+   → "95 años" + ... + "100 y más años"  (open-ended top group)

Population unit: persons. Source CSV uses Spanish number formatting (dots as
thousand separators) for some rows; values may also be plain integers depending
on whether the field is from the post-2021 Censo. Both are handled.
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

PERIOD_MONTH = {
    "enero": "01-01",
    "abril": "04-01",
    "julio": "07-01",
    "octubre": "10-01",
}

# Build age-group bins matching INE ECM table 7947
AGE_BINS = [("<1", ["0 años"]), ("1-4", [f"{i} año" if i == 1 else f"{i} años" for i in range(1, 5)])]
for lo in range(5, 95, 5):
    AGE_BINS.append((f"{lo}-{lo+4}", [f"{i} años" for i in range(lo, lo + 5)]))
AGE_BINS.append(
    # "100 y más años" is the open-ended top group; "100 años" is a single year
    # already included in it — exclude "100 años" to avoid double-counting.
    ("95+", [f"{i} años" for i in range(95, 100)] + ["100 y más años"])
)

AGE_TO_BIN = {}
for bin_label, members in AGE_BINS:
    for m in members:
        AGE_TO_BIN[m] = bin_label


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


def main(in_path: str) -> int:
    long_rows = []
    bin_totals: dict = {}  # (year, sex, bin) -> pop, July 1 only

    with open(in_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        for row in reader:
            if len(row) < 4:
                continue
            age_raw, sex_raw, periodo, value_raw = row[0], row[1], row[2], row[3]
            sex = SEX_MAP.get(sex_raw)
            if sex is None:
                continue
            pp = parse_periodo(periodo)
            if pp is None:
                continue
            year, month_day = pp
            value = parse_value(value_raw)
            if value is None:
                continue

            long_rows.append(
                {
                    "year": year,
                    "ref_date": f"{year}-{month_day}",
                    "sex": sex,
                    "age_label": age_raw.strip(),
                    "population": value,
                }
            )

            # Only July 1 contributes to mid-year 5-yr bins.
            if month_day != "07-01":
                continue
            age_bin = AGE_TO_BIN.get(age_raw.strip())
            if age_bin is None:
                continue
            bin_totals[(year, sex, age_bin)] = bin_totals.get((year, sex, age_bin), 0) + value

    out_long = "data/processed/population_spain_estimates.csv"
    long_rows.sort(key=lambda r: (r["year"], r["ref_date"], r["sex"], r["age_label"]))
    with open(out_long, "w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["year", "ref_date", "sex", "age_label", "population"]
        )
        w.writeheader()
        w.writerows(long_rows)
    print(f"{out_long}: {len(long_rows)} rows")

    out_bin = "data/processed/population_spain_midyear_5yr.csv"
    with open(out_bin, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "sex", "age_group", "population_july1"])
        for (y, s, b), v in sorted(bin_totals.items()):
            w.writerow([y, s, b, v])
    print(f"{out_bin}: {len(bin_totals)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
