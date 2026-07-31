"""Parse INE Table 28857 — Convicted persons for sexual crimes by sex, age, and nationality.

Source: https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/28857.csv?nocab=1

Coverage: 2017–2025 (adults convicted, Chapter 8 "Contra la libertad e
indemnidad sexuales", no crime-subtype split — headline sexual-crime total
only).
Breakdown: sex × age (9 bands: 18-20, 21-25, 26-30, 31-35, 36-40, 41-50,
51-60, 61-70, 71+) × nationality (continent-level groups only — "De Africa"/
"De América"/etc, NOT country-level; Morocco and Algeria cannot be isolated
from this table) × year.

This is the general-population reference age-specific offending-rate curve
used by `compute_age_standardized_rate.py` (T78) for the H3 age-composition
hypothesis test: the "Total"/"Total" (all sexes, all nationalities) row set
gives Spain's overall age-specific sexual-crime conviction count, which
combined with single-year population-by-age (`population_spain_estimates.csv`)
yields a reference rate curve that can be applied to any group's own age
distribution — including Morocco's/Algeria's, from Eurostat's real age band
cross in `migration_spain.csv` — without needing this table to itself carry a
country-level nationality split (it doesn't).

The INE CSV uses semicolons as field separators and Spanish number formatting
(dot as thousands separator, comma as decimal separator).

Output:
    data/processed/ine_condenados_28857_age_nationality.csv
        One row per (sex, nationality_group, age_band, year) with count.
"""

import pandas as pd
import requests
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "data" / "processed"
OUT_CSV = OUT_DIR / "ine_condenados_28857_age_nationality.csv"

INE_URL = "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/28857.csv?nocab=1"

SEX_LABELS = {"Total": "all", "Hombres": "male", "Mujeres": "female"}

NATIONALITY_LABELS = {
    "Total": "total",
    "Española": "espanola",
    "País de la UE27_2020 sin España": "ue27_excl_espana",
    "País de la UE28 sin España": "ue28_excl_espana",
    "País de Europa menos UE27_2020": "europa_no_ue27",
    "País de Europa menos UE28": "europa_no_ue28",
    "De Africa": "africa",
    "De América": "america",
    "De Asia": "asia",
    "De Oceanía": "oceania",
}

AGE_LABELS = {
    "Total": "total",
    "De 18 a 20 años": "18-20",
    "De 21 a 25 años": "21-25",
    "De 26 a 30 años": "26-30",
    "De 31 a 35 años": "31-35",
    "De 36 a 40 años": "36-40",
    "De 41 a 50 años": "41-50",
    "De 51 a 60 años": "51-60",
    "De 61 a 70 años": "61-70",
    "71 y más años": "71+",
}


def fetch_raw(url: str = INE_URL) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content.decode("utf-8-sig")


def parse_raw(text: str) -> pd.DataFrame:
    df = pd.read_csv(
        StringIO(text),
        sep=";",
        thousands=".",
        decimal=",",
        encoding="utf-8-sig",
    )
    df.columns = ["sex", "nationality", "age", "year", "count"]
    df["sex"] = df["sex"].str.strip().map(SEX_LABELS).fillna(df["sex"])
    df["nationality"] = df["nationality"].str.strip().map(NATIONALITY_LABELS).fillna(df["nationality"])
    df["age"] = df["age"].str.strip().map(AGE_LABELS).fillna(df["age"])
    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    df = df.dropna(subset=["count"])
    df["count"] = df["count"].astype(int)
    return df.sort_values(["year", "nationality", "age", "sex"]).reset_index(drop=True)


def validate(df: pd.DataFrame) -> list[str]:
    """Cross-check: for each (sex, year), the sum of named age bands must
    equal the 'total' age row, and the sum of named nationality groups must
    equal the 'total' nationality row (V12)."""
    errors = []
    for year in sorted(df["year"].unique()):
        for sex in ("all", "male", "female"):
            sub = df[(df["year"] == year) & (df["sex"] == sex) & (df["nationality"] == "total")]
            total_row = sub[sub["age"] == "total"]
            age_rows = sub[sub["age"] != "total"]
            if total_row.empty or age_rows.empty:
                continue
            expected = int(total_row["count"].iloc[0])
            actual = int(age_rows["count"].sum())
            if abs(actual - expected) > 5:
                errors.append(
                    f"{year}/{sex}: age sub-totals {actual} != header total {expected} (diff {actual - expected})"
                )
    return errors


def main():
    print("Fetching INE Table 28857 (Condenados por delitos sexuales según sexo, edad y nacionalidad)...")
    text = fetch_raw()
    df = parse_raw(text)
    print(f"Rows: {len(df)}; years: {sorted(df['year'].unique())}")

    errors = validate(df)
    if errors:
        print("VALIDATION WARNINGS:")
        for e in errors:
            print(f"  ⚠ {e}")
    else:
        print("✓ Validation passed (age sub-totals reconcile to header total)")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"Saved -> {OUT_CSV.name} ({len(df)} rows)")

    print("\n=== Total convictions by age band, all nationalities, sex=all ===")
    ref = df[(df["sex"] == "all") & (df["nationality"] == "total") & (df["age"] != "total")]
    pivot = ref.pivot_table(values="count", index="age", columns="year", aggfunc="sum")
    print(pivot.to_string())


if __name__ == "__main__":
    main()
