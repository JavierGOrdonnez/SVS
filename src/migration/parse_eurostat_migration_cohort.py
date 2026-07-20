"""Extract age x sex x origin-nationality flow/stock rows for Morocco (MA) and
Algeria (DZ) from Eurostat bulk data, and append them to migration_spain.csv.

Built for T41 (cohort-tenure crime-rate hypothesis test): the existing
migration_spain.csv only carries age_group, sex, and country_of_origin as
mutually-exclusive marginal slices -- never jointly. INE's own cross-tabulated
tables (24290 flow, 36825 stock) have the joint cross but stop at 2021/2022
respectively. Eurostat's country-level citizenship tables carry the same
joint cross (5-yr age bands x sex x citizenship) through 2024 (flow) / 2025
(stock), so no extrapolation is needed.

Source (download manually -- large bulk files, not committed):
  Flow:  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/migr_imm1ctz?format=TSV&compressed=true
  Stock: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/migr_pop1ctz?format=TSV&compressed=true
  (gunzip before passing to this script)

Usage:
    python src/migration/parse_eurostat_migration_cohort.py <migr_imm1ctz.tsv> <migr_pop1ctz.tsv>

Appends new rows to data/raw/migration_spain.csv (idempotent: rows for
citizen in {MA, DZ} with a non-'all' age_group are dropped and regenerated
each run, rather than duplicated).
"""
import csv
import re
import sys

CITIZENS = ["MA", "DZ"]
AGE_BANDS_5YR = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59"]
SEX_MAP = {"M": "male", "T": "all"}

CSV_PATH = "data/raw/migration_spain.csv"

_VALUE_RE = re.compile(r"^-?\d+")


def _parse_value(raw: str):
    """Eurostat bulk cells are '<number> <flags>' or ': <flags>' for missing
    (flags e.g. 'b'=break, 'e'=estimated, 'p'=provisional, '@N'=annotation)."""
    m = _VALUE_RE.match(raw.strip())
    if m is None:
        return None
    return int(m.group(0))


def _read_bulk_tsv(path: str):
    """Yield (dims: dict, year: int, value: int|None) for every data cell."""
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        dim_names = header[0].split(",")[:-1]  # last dim col header is "dim\\TIME_PERIOD"
        dim_names.append(header[0].split("\\")[0].split(",")[-1])
        years = [int(y.strip()) for y in header[1:]]
        for line in f:
            parts = line.rstrip("\n").split("\t")
            dims = dict(zip(dim_names, parts[0].split(",")))
            for year, raw in zip(years, parts[1:]):
                yield dims, year, _parse_value(raw)


def extract_flow(path: str) -> list[dict]:
    rows = []
    for dims, year, value in _read_bulk_tsv(path):
        if dims.get("citizen") not in CITIZENS or dims.get("geo") != "ES":
            continue
        if dims.get("agedef") != "COMPLET" or dims.get("unit") != "NR":
            continue
        sex = SEX_MAP.get(dims.get("sex"))
        if sex is None:
            continue
        age = dims.get("age")
        if age == "TOTAL":
            age_group = "all"
        elif age and age.startswith("Y") and "-" in age and age[1:] in AGE_BANDS_5YR:
            age_group = age[1:]
        else:
            continue
        if value is None:
            continue
        rows.append({
            "series": "flow_immigration_from_abroad", "year": year, "value": value,
            "sex": sex, "age_group": age_group, "origin": dims["citizen"],
            "source_name": "Eurostat", "source_table": "migr_imm1ctz",
            "source_publication": "Eurostat migr_imm1ctz bulk download (immigration by age, sex, citizenship; agedef=COMPLET)",
            "source_url": "https://ec.europa.eu/eurostat/databrowser/view/migr_imm1ctz/default/table?lang=en",
            "confidence": "high",
            "notes": "T41 cohort-denominator extraction: 5yr age band x sex, real (non-approximated) origin-country cross",
        })
    return rows


def extract_stock(path: str) -> list[dict]:
    rows = []
    for dims, year, value in _read_bulk_tsv(path):
        if dims.get("citizen") not in CITIZENS or dims.get("geo") != "ES":
            continue
        if dims.get("unit") != "NR":
            continue
        sex = SEX_MAP.get(dims.get("sex"))
        if sex is None:
            continue
        age = dims.get("age")
        if age == "TOTAL":
            age_group = "all"
        elif age and age.startswith("Y") and "-" in age and age[1:] in AGE_BANDS_5YR:
            age_group = age[1:]
        else:
            continue
        if value is None:
            continue
        rows.append({
            "series": "stock_foreign_nationality", "year": year, "value": value,
            "sex": sex, "age_group": age_group, "origin": dims["citizen"],
            "source_name": "Eurostat", "source_table": "migr_pop1ctz",
            "source_publication": "Eurostat migr_pop1ctz bulk download (population stock by age, sex, citizenship, 1 Jan)",
            "source_url": "https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table?lang=en",
            "confidence": "high",
            "notes": "T41 cohort-denominator extraction: 5yr age band x sex, real (non-approximated) nationality cross",
        })
    return rows


def main(flow_path: str, stock_path: str) -> int:
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        existing = list(reader)

    kept = [
        r for r in existing
        if not (r["country_of_origin"] in CITIZENS and r["age_group"] != "all")
    ]
    dropped = len(existing) - len(kept)

    new_rows = extract_flow(flow_path) + extract_stock(stock_path)
    next_id = max(int(r["row_id"]) for r in existing) + 1
    for r in new_rows:
        kept.append({
            "row_id": next_id, "series": r["series"], "metric": "count",
            "year": r["year"], "value": r["value"], "unit": "persons",
            "sex": r["sex"], "age_group": r["age_group"],
            "nationality": r["origin"], "country_of_origin": r["origin"],
            "region": "national", "source_name": r["source_name"],
            "source_publication": r["source_publication"],
            "source_table": r["source_table"], "source_url": r["source_url"],
            "confidence": r["confidence"], "notes": r["notes"],
        })
        next_id += 1

    kept.sort(key=lambda r: int(r["row_id"]))
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(kept)

    print(f"dropped {dropped} stale joint rows, added {len(new_rows)} new rows -> {CSV_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
