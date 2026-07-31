"""Parse INE Table 28716 — Convicted criminals by crime type and nationality.

Source: https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/28716.csv?nocab=1

Coverage: 2017–2024 (adults convicted)
Breakdown: Crime type (7-bis Trata, 8 Libertad Sexual) × nationality group × year

The INE CSV uses semicolons as field separators and Spanish number formatting
(dot as thousands separator, comma as decimal separator).

Outputs:
    data/processed/ine_condenados_28716_sexual_crimes.csv
        One row per (crime_category, nationality, year) with count.

    data/processed/ine_condenados_28716_nationality_pct.csv
        Derived: % of each nationality group per year for Chapter 8.
"""

import sys
import csv
import requests
import pandas as pd
from pathlib import Path
from io import StringIO

ROOT = Path(__file__).parent.parent.parent
OUT_DIR = ROOT / "data" / "processed"

INE_URL = "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/28716.csv?nocab=1"

NATIONALITY_LABELS = {
    "Española": "española",
    "País de la UE27_2020 sin España": "ue27_excl_espana",
    "País de la UE28 sin España": "ue28_excl_espana",
    "País de Europa menos UE27_2020": "europa_no_ue27",
    "País de Europa menos UE28": "europa_no_ue28",
    "De Africa": "africa",
    "De América": "america",
    "De Asia": "asia",
    "De Oceanía": "oceania",
    "Total": "total",
}

CRIME_LABELS = {
    "8 Contra la libertad e indemnidad sexuales": "cap8_total",
    "8.1 Agresiones sexuales": "agresiones_sexuales",
    "8.1.1 Agresión sexual": "agresion_sexual",
    "8.1.2 Violación": "violacion",
    "8.2 Abusos sexuales": "abusos_sexuales",
    "8.2 BIS Abusos y agresiones sexuales a menores de 16 años": "abusos_agresiones_menores16",
    "8.3 Acoso sexual": "acoso_sexual",
    "8.4 Exhibicionismo y provocación sexual": "exhibicionismo",
    "8.5 Prostitución y corrupción menores": "prostitucion_menores",
}


def fetch_raw(url: str = INE_URL) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content.decode("utf-8-sig")


def parse_raw(text: str) -> pd.DataFrame:
    """Parse the INE CSV into a tidy DataFrame."""
    # INE format: semicolon delimited, dot=thousands sep, comma=decimal sep
    df = pd.read_csv(
        StringIO(text),
        sep=";",
        thousands=".",
        decimal=",",
        encoding="utf-8-sig",
    )
    df.columns = ["nivel1", "nivel2", "nivel3", "nivel4", "nationality", "year", "count"]
    df["count"] = pd.to_numeric(df["count"], errors="coerce")
    return df


def extract_sexual_crimes(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to Chapter 8 (sexual crimes) and map labels."""
    ch8 = df[df["nivel2"].str.startswith("8", na=False)].copy()

    # Determine crime category from finest available level
    def crime_key(row):
        for col in ("nivel4", "nivel3", "nivel2"):
            v = row[col]
            if pd.notna(v) and str(v).strip():
                return str(v).strip()
        return "unknown"

    ch8["crime_key"] = ch8.apply(crime_key, axis=1)
    ch8["crime_label"] = ch8["crime_key"].map(CRIME_LABELS).fillna(ch8["crime_key"])
    ch8["nationality_label"] = ch8["nationality"].map(NATIONALITY_LABELS).fillna(ch8["nationality"])

    # Include chapter-total rows too (nivel3 and nivel4 both null)
    result = ch8[["year", "crime_label", "nationality_label", "count"]].copy()
    result = result.dropna(subset=["count"])
    result = result.sort_values(["year", "crime_label", "nationality_label"])
    result = result.reset_index(drop=True)
    return result


def compute_nationality_pct(df: pd.DataFrame) -> pd.DataFrame:
    """For each year, compute % of each nationality out of cap8 total."""
    cap8 = df[df["crime_label"] == "cap8_total"].copy()
    totals = cap8[cap8["nationality_label"] == "total"][["year", "count"]].rename(
        columns={"count": "total_convicted"}
    )
    pct = cap8.merge(totals, on="year")
    pct = pct[pct["nationality_label"] != "total"].copy()
    pct["pct_of_total"] = (pct["count"] / pct["total_convicted"] * 100).round(1)
    pct = pct.sort_values(["year", "nationality_label"])

    # Also consolidate EU/non-EU Europe series (INE changed classification post-2020)
    def continent_group(nat):
        if nat in ("ue27_excl_espana", "ue28_excl_espana"):
            return "ue_excl_espana"
        if nat in ("europa_no_ue27", "europa_no_ue28"):
            return "europa_no_ue"
        return nat

    pct["nationality_group"] = pct["nationality_label"].map(continent_group)
    grouped = (
        pct.groupby(["year", "nationality_group"])
        .agg(count=("count", "sum"), total_convicted=("total_convicted", "first"))
        .reset_index()
    )
    grouped["pct_of_total"] = (grouped["count"] / grouped["total_convicted"] * 100).round(1)
    return grouped.sort_values(["year", "nationality_group"])


def validate(df: pd.DataFrame) -> list[str]:
    """Check that nationality sub-totals reconcile with 'total' rows."""
    errors = []
    cap8 = df[df["crime_label"] == "cap8_total"]
    for year in sorted(cap8["year"].unique()):
        total_row = cap8[(cap8["year"] == year) & (cap8["nationality_label"] == "total")]
        sub_rows = cap8[(cap8["year"] == year) & (cap8["nationality_label"] != "total")]
        if total_row.empty or sub_rows.empty:
            continue
        expected = float(total_row["count"].iloc[0])
        actual = float(sub_rows["count"].sum())
        if abs(actual - expected) > 5:  # allow rounding of 5
            errors.append(
                f"Year {year}: sub-totals {actual:.0f} ≠ header total {expected:.0f} "
                f"(diff {actual - expected:.0f})"
            )
    return errors


def main():
    print("Fetching INE Table 28716 (Condenados por delito y nacionalidad)...")
    text = fetch_raw()
    df_raw = parse_raw(text)

    print(f"Raw rows: {len(df_raw)}; years: {sorted(df_raw['year'].dropna().astype(int).unique())}")

    df_sex = extract_sexual_crimes(df_raw)
    pct_df = compute_nationality_pct(df_sex)

    errors = validate(df_sex)
    if errors:
        print("VALIDATION WARNINGS:")
        for e in errors:
            print(f"  ⚠ {e}")
    else:
        print("✓ Validation passed (sub-totals reconcile)")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out1 = OUT_DIR / "ine_condenados_28716_sexual_crimes.csv"
    out2 = OUT_DIR / "ine_condenados_28716_nationality_pct.csv"
    df_sex.to_csv(out1, index=False)
    pct_df.to_csv(out2, index=False)
    print(f"Saved → {out1.name} ({len(df_sex)} rows)")
    print(f"Saved → {out2.name} ({len(pct_df)} rows)")

    # Print summary table
    print("\n=== % convicted by nationality group — Chapter 8 Sexual Crimes ===")
    pivot = pct_df.pivot_table(
        values="pct_of_total", index="nationality_group", columns="year", aggfunc="sum"
    ).round(1)
    print(pivot.to_string())

    print("\n=== Agresiones sexuales convictions by nationality (abs) ===")
    ag = df_sex[df_sex["crime_label"] == "agresiones_sexuales"]
    ag_pivot = ag.pivot_table(
        values="count", index="nationality_label", columns="year", aggfunc="sum"
    )
    print(ag_pivot.to_string())


if __name__ == "__main__":
    main()
