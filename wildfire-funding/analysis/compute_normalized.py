"""Join wff_spending.csv with wff_denominators.csv and compute normalized
wildfire-funding figures per CCAA: euros per 100,000 inhabitants, euros per
km^2 of forest area, and (where the spend year and the total-budget year are
within 1 of each other) % of the region's own total budget. See ../SPEC.md
T6/T7 and V3 (never publish a normalized figure without the raw amount +
denominator alongside it).

Population is a 2024 snapshot; forest area is a 2019 snapshot (MITECO
Anuario de Estadística Forestal, table 6.1.1); total budgets are each
region's own most recent figure (2025 or 2026, `total_budget_year` per
row). None of these move fast enough year-to-year to invalidate a same-year
comparison, but for older spend rows (Andalucía 2020-2024) the population/
forest-area/budget-share denominators are for a later year than the spend
itself — that mismatch is real and is called out in the report, not hidden.
"""

import pandas as pd

DATA_DIR = "../data/raw"
REPORT_PATH = "../reports/wff_first_pass_2025_2026.md"


def main() -> None:
    spending = pd.read_csv(f"{DATA_DIR}/wff_spending.csv")
    denom = pd.read_csv(f"{DATA_DIR}/wff_denominators.csv")

    spending = spending[spending["amount_eur"].notna()].copy()
    df = spending.merge(denom, on="ccaa", how="left")

    df["eur_per_100k_hab"] = df["amount_eur"] / (df["population"] / 100_000)
    df["eur_per_km2_forest"] = df["amount_eur"] / df["forest_area_km2"]

    year_gap = (df["year"] - df["total_budget_year"]).abs()
    df["pct_of_total_budget"] = (df["amount_eur"] / df["total_budget_eur"] * 100).where(
        year_gap <= 1
    )

    latest = df.sort_values("year").groupby("ccaa", as_index=False).tail(1)
    latest = latest.sort_values("eur_per_km2_forest", ascending=False)

    history = df[df.groupby("ccaa")["ccaa"].transform("size") > 1].sort_values(
        ["ccaa", "year"]
    )

    lines = [
        "# WFF — First-pass wildfire-funding comparison",
        "",
        "Scaffold-stage output — see `../SPEC.md` C2/C3/C7 for why this is a first",
        "pass, not a finished result: spending figures are `confidence=low` and",
        "several carry unresolved scope/source conflicts (see `notes` column in",
        "`wff_spending.csv`). Canarias is excluded (no consolidated regional",
        "total found). `pct_of_total_budget` is blank whenever the spend year and",
        "the region's total-budget year are more than 1 year apart (most of the",
        "historical Andalucía rows below) — better a gap than a misleading ratio.",
        "",
        "## Latest year per CCAA, normalized three ways",
        "",
        "| CCAA | Year | Spend (€M) | Coverage | € / 100k hab | € / km² forest | % of own budget |",
        "|---|---|---|---|---|---|---|",
    ]
    for _, r in latest.iterrows():
        pct = f"{r['pct_of_total_budget']:.3f}%" if pd.notna(r["pct_of_total_budget"]) else "—"
        lines.append(
            f"| {r['ccaa']} | {int(r['year'])} | {r['amount_eur']/1e6:,.1f} | "
            f"{r['coverage']} | {r['eur_per_100k_hab']:,.0f} | "
            f"{r['eur_per_km2_forest']:,.0f} | {pct} |"
        )

    lines += [
        "",
        "## Time series (CCAAs with more than one sourced year)",
        "",
        "Only Andalucía (Plan INFOCA, 2020-2026) and Castilla-La Mancha (Plan",
        "INFOCAM, 2025-2026) have more than one sourced year so far — everything",
        "else is still a single snapshot. See `SPEC.md` T8 for extending this.",
        "",
        "| CCAA | Year | Spend (€M) | € / 100k hab | € / km² forest |",
        "|---|---|---|---|---|",
    ]
    for _, r in history.iterrows():
        lines.append(
            f"| {r['ccaa']} | {int(r['year'])} | {r['amount_eur']/1e6:,.1f} | "
            f"{r['eur_per_100k_hab']:,.0f} | {r['eur_per_km2_forest']:,.0f} |"
        )

    lines += [
        "",
        "## Reading notes",
        "",
        "- Ranking absolute spend is not the same ranking as any of the three",
        "  normalizations — that's the point of computing them (README.md's",
        "  core motivation).",
        "- `coverage=partial` rows (Cataluña, Islas Baleares) understate the true",
        "  figure — their normalized values are floors, not full pictures.",
        "- Andalucía's own series (171.9M → 175.1M → 223M → 244M → 300M,",
        "  2020-2026) shows nominal spend nearly doubling in six years — but this",
        "  is *budgeted/announced* spend, not audited *executed* spend; the two",
        "  can differ substantially once a season's actual fire severity forces",
        "  extraordinary in-year credits. No region's liquidación (executed)",
        "  figure has been sourced yet — see `SPEC.md` T9.",
        "- Every absolute-spend row above has at least one unresolved",
        "  conflicting/alternate figure documented in `wff_spending.csv`'s",
        "  `notes` column — treat this table as directional, not final, until",
        "  T2/T3 trace each figure to its primary budget-law source.",
    ]

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {REPORT_PATH} ({len(latest)} regions, {len(history)} history rows)")


if __name__ == "__main__":
    main()
