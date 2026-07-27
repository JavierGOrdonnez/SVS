"""Join wff_spending.csv with wff_denominators.csv and compute normalized
wildfire-funding figures per CCAA: euros per 100,000 inhabitants and euros
per km^2 of forest area. See ../SPEC.md T7 and V3 (never publish a
normalized figure without the raw amount + denominator alongside it).

Population is a 2024 snapshot; spending rows are 2025/2026. Forest area is
a 2019 snapshot (MITECO Anuario de Estadística Forestal, table 6.1.1) —
none of these move fast enough year-to-year to invalidate the comparison,
but the mismatch is real and is carried into the report, not hidden.
"""

import pandas as pd

DATA_DIR = "../data/raw"
REPORT_PATH = "../reports/wff_first_pass_2025_2026.md"


def main() -> None:
    spending = pd.read_csv(f"{DATA_DIR}/wff_spending.csv")
    denom = pd.read_csv(f"{DATA_DIR}/wff_denominators.csv")

    spending = spending[spending["amount_eur"].notna()].copy()
    df = spending.merge(denom, on="ccaa", how="left", suffixes=("_spend", "_denom"))

    df["eur_per_100k_hab"] = df["amount_eur"] / (df["population"] / 100_000)
    df["eur_per_km2_forest"] = df["amount_eur"] / df["forest_area_km2"]

    df = df.sort_values("eur_per_km2_forest", ascending=False)

    lines = [
        "# WFF — First-pass normalized comparison (2025/2026 spend, 2024 population, 2019 forest area)",
        "",
        "Scaffold-stage output — see `../SPEC.md` C2/C3/C7 for why this is a first",
        "pass, not a finished result: spending figures are `confidence=low` and",
        "several carry unresolved scope/source conflicts (see `notes` column in",
        "`wff_spending.csv`). Canarias is excluded (no consolidated regional",
        "total found). Total-CCAA-budget normalization (% of own budget) is not",
        "yet computed — `total_budget_eur` is still pending (T6).",
        "",
        "| CCAA | Year | Spend (€M) | Coverage | € / 100k hab | € / km² forest |",
        "|---|---|---|---|---|---|",
    ]
    for _, r in df.iterrows():
        lines.append(
            f"| {r['ccaa']} | {int(r['year_spend'])} | {r['amount_eur']/1e6:,.1f} | "
            f"{r['coverage']} | {r['eur_per_100k_hab']:,.0f} | {r['eur_per_km2_forest']:,.0f} |"
        )

    lines += [
        "",
        "## Reading notes",
        "",
        "- Ranking absolute spend (Andalucía, Comunidad Valenciana, Galicia at the",
        "  top) is not the same ranking as either normalization — that's the",
        "  point of computing them (README.md's core motivation).",
        "- `coverage=partial` rows (Cataluña, Islas Baleares) understate the true",
        "  figure — their normalized values are floors, not full pictures.",
        "- Every absolute-spend row above has at least one unresolved",
        "  conflicting/alternate figure documented in `wff_spending.csv`'s",
        "  `notes` column — treat this table as directional, not final, until",
        "  T2/T3 trace each figure to its primary budget-law source.",
    ]

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {REPORT_PATH} ({len(df)} regions)")


if __name__ == "__main__":
    main()
