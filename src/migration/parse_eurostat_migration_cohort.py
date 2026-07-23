"""Extract age x sex x origin-nationality flow/stock rows for the top-35
foreign nationalities in Spain plus Spanish nationals (ES) from Eurostat
data, and append them to migration_spain.csv.

Replaces the previous MA/DZ-only extraction (T41). Now covers ~94% of
foreign stock by nationality and provides the real joint age(5yr) x sex x
citizenship cross needed for:
  - Feminicide rate denominators (T66): per-year sex-specific foreign pop
  - Crime cohort analysis (T43/T44): per-nationality age-band x sex stock
  - Immigration flow analysis: sex-disaggregated inflows by nationality

Stock extraction also carries the `Y_LT15`/`Y_GE65`/`Y_GE85` aggregate age
bands (mapped to age_group `0-14`/`65+`/`85+`) alongside 5yr bands through
`80-84`, needed by the age-pyramid panels (T69/T70) to derive a 0-9 band as
`0-14 minus 10-14` and an 80+ band as `80-84 plus 85+`.

Data source: Eurostat SDMX-JSON API (migr_pop1ctz stock, migr_imm1ctz flow)
  Stock: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/migr_pop1ctz
  Flow:  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/migr_imm1ctz

Input files are pre-downloaded JSONL (one JSON object per line) saved from
the Eurostat SDMX-JSON API.  Each line has:
  {"citizen": "MA", "citizen_name": "Morocco", "age": "TOTAL",
   "sex": "F", "year": 2025, "value": 402512}

Download procedure (stock example — flow analogous):
  curl -sL "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/migr_pop1ctz/A.{CITIZENS}.AGE_BANDS.NR.F+M+T.ES?format=JSON&compressed=false" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); ..."  # decode to JSONL

Usage:
    python src/migration/parse_eurostat_migration_cohort.py <flow.jsonl> <stock.jsonl>

Appends new rows to data/raw/migration_spain.csv (idempotent: rows with
source_name=Eurostat for any nationality in CITIZENS are dropped and
regenerated each run).
"""
import csv
import json
import re
import sys

# Top-35 nationalities by 2025 stock share (94.4% of foreign pop), plus ES
# for Spanish-female denominator.  Grouped by region for display:
#   Africa:       MA DZ SN NG ML
#   Latin America: CO VE PE HN AR EC PY BR BO CU NI DO
#   Anglo:        UK US
#   EU:           RO IT DE FR PT BG NL PL SE IE
#   Non-EU EU:    UA RU
#   Asia:         CN PK IN BD PH
#   Long tail:    GQ GN GH GM CL MX UY LT MD CH FI NO DK BE AT
CITIZENS = [
    "ES",  # Spanish nationals (feminicide denominator)
    # Africa
    "MA", "DZ", "SN", "NG", "ML",
    # Latin America
    "CO", "VE", "PE", "HN", "AR", "EC", "PY", "BR", "BO", "CU", "NI", "DO",
    # Anglo
    "UK", "US",
    # EU
    "RO", "IT", "DE", "FR", "PT", "BG", "NL", "PL", "SE", "IE",
    # Non-EU Europe
    "UA", "RU",
    # Asia
    "CN", "PK", "IN", "BD", "PH",
    # Long tail (>0.1% each)
    "GQ", "GN", "GH", "GM", "CL", "MX", "UY", "LT", "MD", "CH",
    "FI", "NO", "DK", "BE", "AT",
]

AGE_BANDS_5YR = [
    "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59",
    "60-64", "65-69", "70-74", "75-79", "80-84",
]
SEX_MAP = {"M": "male", "F": "female", "T": "all"}

CSV_PATH = "data/raw/migration_spain.csv"


def _load_jsonl(path: str) -> list[dict]:
    """Read a JSONL file (one JSON object per line)."""
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _age_to_group(age: str) -> str | None:
    """Map Eurostat age code to CSV age_group.  Returns None for skip."""
    if age == "TOTAL":
        return "all"
    if age == "Y_LT15":
        return "0-14"
    if age == "Y_GE65":
        return "65+"
    if age == "Y_GE85":
        return "85+"
    if age.startswith("Y") and "-" in age:
        band = age[1:]
        if band in AGE_BANDS_5YR:
            return band
    return None


def extract_flow(rows: list[dict]) -> list[dict]:
    """Extract immigration flow rows from decoded Eurostat data."""
    out = []
    for r in rows:
        if r["citizen"] not in CITIZENS:
            continue
        sex = SEX_MAP.get(r["sex"])
        if sex is None:
            continue
        age_group = _age_to_group(r["age"])
        if age_group is None:
            continue
        val = r.get("value")
        if val is None:
            continue
        out.append({
            "series": "flow_immigration_from_abroad",
            "year": r["year"], "value": int(val),
            "sex": sex, "age_group": age_group, "origin": r["citizen"],
            "source_name": "Eurostat", "source_table": "migr_imm1ctz",
            "source_publication": (
                "Eurostat migr_imm1ctz (immigration by age, sex, citizenship; "
                "agedef=COMPLET)"
            ),
            "source_url": (
                "https://ec.europa.eu/eurostat/databrowser/view/"
                "migr_imm1ctz/default/table?lang=en"
            ),
            "confidence": "high",
            "notes": (
                "T66 expansion: joint age(5yr) x sex x citizenship cross "
                "for top-35 nationalities + ES"
            ),
        })
    return out


def extract_stock(rows: list[dict]) -> list[dict]:
    """Extract population stock rows from decoded Eurostat data."""
    out = []
    for r in rows:
        if r["citizen"] not in CITIZENS:
            continue
        sex = SEX_MAP.get(r["sex"])
        if sex is None:
            continue
        age_group = _age_to_group(r["age"])
        if age_group is None:
            continue
        val = r.get("value")
        if val is None:
            continue
        out.append({
            "series": "stock_nationality",
            "year": r["year"], "value": int(val),
            "sex": sex, "age_group": age_group, "origin": r["citizen"],
            "source_name": "Eurostat", "source_table": "migr_pop1ctz",
            "source_publication": (
                "Eurostat migr_pop1ctz (population stock by age, sex, "
                "citizenship, 1 Jan)"
            ),
            "source_url": (
                "https://ec.europa.eu/eurostat/databrowser/view/"
                "migr_pop1ctz/default/table?lang=en"
            ),
            "confidence": "high",
            "notes": (
                "T66 expansion: joint age(5yr) x sex x citizenship cross "
                "for top-35 nationalities + ES"
            ),
        })
    return out


def main(flow_path: str, stock_path: str) -> int:
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        existing = list(reader)

    # Drop ALL existing Eurostat-sourced rows (idempotent regeneration).
    # Also drop old stock_foreign_nationality rows for per-nationality codes
    # now replaced by stock_nationality — but keep the INE-sourced
    # "nationality=foreign" aggregate (used by feminicide rate computation).
    eurostat_citizens = set(CITIZENS) - {"ES"}  # ES rows replace INE spanish
    kept = []
    dropped = 0
    for r in existing:
        is_eurostat = r["source_name"] == "Eurostat"
        is_old_per_nat = (
            r["series"] == "stock_foreign_nationality"
            and r["country_of_origin"] in eurostat_citizens
        )
        if is_eurostat or is_old_per_nat:
            dropped += 1
            continue
        kept.append(r)

    flow_rows = _load_jsonl(flow_path)
    stock_rows = _load_jsonl(stock_path)
    new_rows = extract_flow(flow_rows) + extract_stock(stock_rows)

    next_id = max((int(r["row_id"]) for r in existing), default=0) + 1
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

    # Summary
    n_citizens_flow = len({r["origin"] for r in new_rows if r["series"] == "flow_immigration_from_abroad"})
    n_citizens_stock = len({r["origin"] for r in new_rows if r["series"] == "stock_nationality"})
    n_female = sum(1 for r in new_rows if r["sex"] == "female")
    print(f"dropped {dropped} old rows, added {len(new_rows)} new rows -> {CSV_PATH}")
    print(f"  flow: {sum(1 for r in new_rows if r['series']=='flow_immigration_from_abroad')} rows, {n_citizens_flow} nationalities")
    print(f"  stock: {sum(1 for r in new_rows if r['series']=='stock_nationality')} rows, {n_citizens_stock} nationalities")
    print(f"  female rows: {n_female}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
