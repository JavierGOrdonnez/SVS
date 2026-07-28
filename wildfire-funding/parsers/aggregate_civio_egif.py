"""Aggregates Civio's EGIF-derived fire-incident dataset (per-fire personnel/
equipment/extinction-cost, 1968-2023) into CCAA x year summaries.

Source: https://data.civio.es/espanaenllamas/fires-map/fires-all.csv
(32.8MB, 296,839 rows) -- not committed to this repo (too large for a git
repo of this size, and it's a stable, directly-refetchable public URL).
Re-download with:
  curl -o /tmp/civio_fires_all.csv "https://data.civio.es/espanaenllamas/fires-map/fires-all.csv"

The `idcomunidad` codes in this dataset are NOT standard INE CCAA codes --
confirmed by cross-referencing each code's most frequent `municipio` values
against known real place names (e.g. code 3's top municipios are all in
Ourense province -> Galicia, not "Asturias" as INE code 3 would imply). See
SPEC.md / private_contractors_and_operations.md for the full story of why
this mapping needed manual verification.
"""

import pandas as pd

RAW_PATH = "/tmp/civio_fires_all.csv"
OUT_PATH = "../data/raw/wff_egif_incidents_by_ccaa_year.csv"

CODE_MAP = {
    1: "País Vasco", 2: "Cataluña", 3: "Galicia", 4: "Andalucía",
    5: "Principado de Asturias", 6: "Cantabria", 7: "La Rioja",
    8: "Región de Murcia", 9: "Comunidad Valenciana", 10: "Aragón",
    11: "Castilla-La Mancha", 12: "Canarias", 13: "Comunidad Foral de Navarra",
    14: "Extremadura", 15: "Islas Baleares", 16: "Comunidad de Madrid",
    17: "Castilla y León", 18: "Ceuta",
}


def main() -> None:
    df = pd.read_csv(RAW_PATH, low_memory=False)
    df["ccaa"] = df["idcomunidad"].map(CODE_MAP)
    df["year"] = df["fecha"].str[:4].astype(int)

    agg = (
        df.groupby(["ccaa", "year"])
        .agg(
            n_fires=("id", "count"),
            superficie_ha=("superficie", "sum"),
            personal_units_sum=("personal", "sum"),
            medios_units_sum=("medios", "sum"),
            gastos_eur_sum=("gastos", "sum"),
            fires_with_gastos_reported=("gastos", lambda s: int((s > 0).sum())),
        )
        .reset_index()
    )
    agg["gastos_coverage_pct"] = (
        agg["fires_with_gastos_reported"] / agg["n_fires"] * 100
    ).round(1)
    agg = agg.sort_values(["ccaa", "year"])
    agg.to_csv(OUT_PATH, index=False)
    print(f"Wrote {OUT_PATH} ({len(agg)} ccaa-year rows)")


if __name__ == "__main__":
    main()
