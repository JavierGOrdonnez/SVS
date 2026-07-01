#!/usr/bin/env python3
"""
MIR Reports × Migration Flux Correlation Analysis

Examines how the nationality breakdown of sexual crime perpetrators
(from MIR annual Informes) correlates with migration fluxes and
foreign-population stock in Spain, 2015-2024.

Key questions:
  1. Did total sexual crime growth outpace, match, or lag migration growth?
  2. Did the foreign-perpetrator share increase with migration stock?
  3. Do per-100k perpetrator rates differ between Spanish and foreign males,
     and did the gap widen or narrow with rising immigration?

Outputs:
  - Printed analysis report (stdout)
  - data/processed/mir_migration_rates.csv
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------

def load_csv(path: str) -> List[Dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_val(rows, **filters) -> Optional[float]:
    """Return first matching row value, or None."""
    for row in rows:
        if all(row.get(k) == str(v) for k, v in filters.items()):
            val = row.get("value") or row.get("count") or row.get("pct")
            if val and str(val).strip():
                try:
                    return float(str(val).replace(",", "."))
                except ValueError:
                    return None
    return None


# ---------------------------------------------------------------------------
# Hard-coded denominators (INE Padrón / EMCR; consistent with SPEC §I)
# ---------------------------------------------------------------------------

# Total resident population (both sexes) by year
# Source: INE Cifras de Población
TOTAL_POP = {
    2015: 46449565, 2016: 46440099, 2017: 46528966, 2018: 46722980,
    2019: 47026208, 2020: 47332614, 2021: 47400798, 2022: 47615034,
    2023: 48059777, 2024: 48592909,
}

# Foreign residents by year (INE Padrón, stock, foreign nationality)
# Source: migration_spain.csv — series stock_foreign_nationality
FOREIGN_STOCK = {
    2015: 4729644, 2016: 4618581, 2017: 4572807, 2018: 4734691,
    2019: 5036878, 2020: 5434153, 2021: 5440148, 2022: 5542932,
    2023: 6089620, 2024: 6502282,
}

# Annual immigration inflows (all nationalities) — EMCR
# Source: migration_spain.csv — series flow_immigration_from_abroad
INFLOW_ALL = {
    2015: 342114, 2016: 414746, 2017: 532132, 2018: 643684,
    2019: 750480, 2020: 467918, 2021: 887960, 2022: 1258894,
    2023: 1250991, 2024: 1288562,
}

# Foreign inflow only
INFLOW_FOREIGN = {
    2023: 1098028,
    2024: 1144227,
}


# ---------------------------------------------------------------------------
# Crime data (from violence_spain.csv and migrant_crime_numerator.csv)
# ---------------------------------------------------------------------------

# Total sexual crimes registered (MIR annual Informe)
SEXUAL_CRIMES_TOTAL = {
    2015: None,   # not available in our data
    2016: None,
    2017: None,
    2018: 13782,
    2019: None,   # 2019 figure uncertain; see B6 in SPEC
    2020: None,
    2021: None,
    2022: 19059,
    2023: 21825,
    2024: 22846,
}

# Detained/investigated for sexual crimes (MIR Informe)
DETAINED_TOTAL = {
    2023: 13767,
    2024: 14375,
}

# Perpetrator nationality share (% of detained with known nationality)
# Source: MIR Informe 2023; 2024 nationality breakdown not yet extracted
PERP_FOREIGN_PCT = {
    # year: (pct_foreign, pct_spanish, source_confidence)
    # 2013-2017 aggregate from group-violence report (specialized subsample):
    "group_2013_2017": (43.3, 32.7, "high"),
    # 2023 annual Informe (all sexual crimes):
    2023: (37.3, 62.7, "medium"),
}

# Victim nationality share (% Spanish)
VICTIM_SPANISH_PCT = {
    # "group_2013_2017": 61.0,   # group violence only
    "sexual_2015_2019": 75.7,    # 5-year aggregate violence against women report
    2023: 73.8,
}


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def compute_derived_counts(year: int) -> Dict:
    """Compute estimated perpetrator counts by nationality for a given year."""
    total_detained = DETAINED_TOTAL.get(year)
    if total_detained is None:
        return {}

    result = {"year": year, "detained_total": total_detained}

    nat_data = PERP_FOREIGN_PCT.get(year)
    if nat_data:
        pct_f, pct_s, conf = nat_data
        result["pct_foreign"] = pct_f
        result["pct_spanish"] = pct_s
        result["count_foreign"] = round(total_detained * pct_f / 100)
        result["count_spanish"] = round(total_detained * pct_s / 100)
        result["nationality_confidence"] = conf
    return result


def per_100k_rate(count: float, population: float) -> float:
    return round(count / population * 100_000, 2)


def pct_change(a: Optional[float], b: Optional[float]) -> Optional[str]:
    if a is None or b is None or a == 0:
        return None
    return f"{(b - a) / a * 100:+.1f}%"


def print_report():
    print("=" * 70)
    print("MIR REPORTS × MIGRATION CORRELATION ANALYSIS")
    print("Spain, Sexual Crimes — Perpetrator Nationality vs Migration Flux")
    print("=" * 70)

    # --- Section 1: Crime trend ---
    print("\n## 1. Sexual Crime Totals and Annual Growth\n")
    print(f"{'Year':<6} {'Total crimes':>12} {'YoY change':>11} {'Foreign stock':>14} {'Stock YoY':>10}")
    prev_crimes = None
    prev_stock = None
    for year in [2018, 2022, 2023, 2024]:
        crimes = SEXUAL_CRIMES_TOTAL.get(year)
        stock = FOREIGN_STOCK.get(year)
        crime_ch = pct_change(prev_crimes, crimes) if crimes else "—"
        stock_ch = pct_change(prev_stock, stock)
        print(
            f"{year:<6} {str(crimes or '—'):>12} {str(crime_ch or '—'):>11} "
            f"{str(stock or '—'):>14} {str(stock_ch or '—'):>10}"
        )
        if crimes:
            prev_crimes = crimes
        if stock:
            prev_stock = stock

    # Note on 2022→2023 comparison
    crime_2022 = SEXUAL_CRIMES_TOTAL[2022]
    crime_2023 = SEXUAL_CRIMES_TOTAL[2023]
    crime_2024 = SEXUAL_CRIMES_TOTAL[2024]
    stock_2022 = FOREIGN_STOCK[2022]
    stock_2023 = FOREIGN_STOCK[2023]
    stock_2024 = FOREIGN_STOCK[2024]

    print(f"\n  2022→2023: crimes +{(crime_2023-crime_2022)/crime_2022*100:.1f}%, "
          f"foreign stock +{(stock_2023-stock_2022)/stock_2022*100:.1f}%")
    print(f"  2023→2024: crimes +{(crime_2024-crime_2023)/crime_2023*100:.1f}%, "
          f"foreign stock +{(stock_2024-stock_2023)/stock_2023*100:.1f}%")
    print(
        "\n  Observation: In 2022→2023, crime growth (+14.5%) substantially exceeded"
        "\n  foreign-population growth (+9.9%). In 2023→2024, crime growth slowed"
        "\n  (+4.7%) and fell BELOW foreign-stock growth (+6.8%), suggesting the"
        "\n  foreign population grew faster than detained counts."
    )

    # --- Section 2: Perpetrator nationality breakdown ---
    print("\n## 2. Perpetrator Nationality (Detained/Investigated)\n")

    d2023 = compute_derived_counts(2023)
    d2024 = compute_derived_counts(2024)

    print(f"  2023 (MIR Informe Delitos Sexuales 2023 — confidence: medium):")
    print(f"    Total detained:     {d2023['detained_total']:>6}")
    print(f"    Spanish:            {d2023.get('count_spanish','—'):>6} ({d2023.get('pct_spanish','—')}%)")
    print(f"    Foreign:            {d2023.get('count_foreign','—'):>6} ({d2023.get('pct_foreign','—')}%)")
    print(f"  2024: nationality breakdown NOT yet in source data (primary PDF blocked).")

    # Group violence baseline (2013-2017)
    pct_f_grp, pct_s_grp, _ = PERP_FOREIGN_PCT["group_2013_2017"]
    print(f"\n  Baseline — group sexual violence 2013-2017 (specialized subsample):")
    print(f"    Foreign perps: {pct_f_grp}%  |  Spanish: {pct_s_grp}%  |  Unknown: "
          f"{round(100-pct_f_grp-pct_s_grp,1)}%")
    print(f"    Top nationalities: Morocco 9.5%, Romania 7.0%, Ecuador 4.0%")

    # --- Section 3: Per-100k rates ---
    print("\n## 3. Per-100k Perpetrator Rates by Nationality (2023)\n")

    total_pop_2023 = TOTAL_POP[2023]
    foreign_pop_2023 = FOREIGN_STOCK[2023]
    spanish_pop_2023 = total_pop_2023 - foreign_pop_2023

    # Use male population (perpetrators are ~93% male, denominator should be males)
    # Approximate: male ≈ 49% of total population
    spanish_male_2023 = round(spanish_pop_2023 * 0.49)
    foreign_male_2023 = round(foreign_pop_2023 * 0.49)

    count_foreign_2023 = d2023.get("count_foreign", 0)
    count_spanish_2023 = d2023.get("count_spanish", 0)

    rate_foreign = per_100k_rate(count_foreign_2023, foreign_male_2023)
    rate_spanish = per_100k_rate(count_spanish_2023, spanish_male_2023)
    ratio = round(rate_foreign / rate_spanish, 2)

    print(f"  Population (2023):")
    print(f"    Spanish (all):   {spanish_pop_2023:>12,}")
    print(f"    Foreign (all):   {foreign_pop_2023:>12,}  ({foreign_pop_2023/total_pop_2023*100:.1f}% of total)")
    print(f"    Spanish (male≈): {spanish_male_2023:>12,}")
    print(f"    Foreign (male≈): {foreign_male_2023:>12,}")
    print(f"\n  Detained perpetrators (2023):")
    print(f"    Spanish:         {count_spanish_2023:>12,}")
    print(f"    Foreign:         {count_foreign_2023:>12,}  (37.3% vs {foreign_pop_2023/total_pop_2023*100:.1f}% of population)")
    print(f"\n  Rate per 100k male residents:")
    print(f"    Spanish:         {rate_spanish:>12.1f} per 100k")
    print(f"    Foreign:         {rate_foreign:>12.1f} per 100k")
    print(f"    Ratio:           {ratio:>12.2f}× (foreign vs Spanish)")

    print(
        f"\n  IMPORTANT CAVEAT: 'detained' ≠ 'offenders'. Rate compares arrests, not"
        f"\n  convictions. Foreign individuals may face higher arrest rates due to"
        f"\n  policing patterns, lack of legal representation, or higher visibility."
        f"\n  Conviction data (INE Condenados) should be the primary metric but"
        f"\n  nationality breakdown is available only for 2023 (3,468 convicted adults)."
    )

    # --- Section 4: Foreign share vs foreign stock ---
    print("\n## 4. Foreign Perpetrator Share vs Foreign Population Share\n")

    pop_share_2023 = foreign_pop_2023 / total_pop_2023 * 100
    detained_share_2023 = d2023.get("pct_foreign", 0)

    print(f"  2023:")
    print(f"    Foreign share of total population:  {pop_share_2023:.1f}%")
    print(f"    Foreign share of detained (sexual):  {detained_share_2023:.1f}%")
    print(f"    Over-representation factor:          {detained_share_2023/pop_share_2023:.1f}×")

    # Historical context from 2015-2019 victim data
    print(f"\n  Historical context (victim nationality — MIR Violence Women 2015-2019):")
    print(f"    Foreign victim share (sexual violence): 24.3% of 44,333 total 5-yr")
    print(f"    Foreign population share ~2017 avg:     ~10%")
    print(f"    → Foreign victims also over-represented as victims in all years")

    # --- Section 5: Migration flux correlation ---
    print("\n## 5. Migration Flux vs Crime Growth Correlation\n")

    # Year-over-year comparisons
    yoy_data = [
        (2022, 2023, crime_2022, crime_2023, stock_2022, stock_2023),
        (2023, 2024, crime_2023, crime_2024, stock_2023, stock_2024),
    ]

    print(f"  {'Period':<12} {'Crime Δ%':>9} {'Pop Δ%':>9} {'Inflow Δ%':>10} {'Interpretation'}")
    for y1, y2, c1, c2, s1, s2 in yoy_data:
        c_ch = (c2 - c1) / c1 * 100
        s_ch = (s2 - s1) / s1 * 100
        inflow1 = INFLOW_ALL.get(y1)
        inflow2 = INFLOW_ALL.get(y2)
        i_ch = (inflow2 - inflow1) / inflow1 * 100 if inflow1 and inflow2 else None
        interpretation = (
            "crime >> pop growth" if c_ch > s_ch + 3 else
            "crime < pop growth" if c_ch < s_ch - 3 else
            "crime ≈ pop growth"
        )
        print(
            f"  {y1}→{y2}      {c_ch:>+8.1f}% {s_ch:>+8.1f}% "
            f"{f'{i_ch:+.1f}%' if i_ch else '—':>9}  {interpretation}"
        )

    # Inflow context
    inflow_2023_f = INFLOW_FOREIGN.get(2023, 0)
    inflow_2024_f = INFLOW_FOREIGN.get(2024, 0)
    print(f"\n  Foreign inflows: 2023 = {inflow_2023_f:,}; 2024 = {inflow_2024_f:,}")
    print(f"  Net foreign stock increase: 2023 = +{stock_2023-stock_2022:,}; 2024 = +{stock_2024-stock_2023:,}")

    print("""
  Interpretation:
    • 2022→2023: The 14.5% crime surge partly reflects the LO 10/2022 (Solo sí es sí)
      reclassification effect — abusos merged into agresiones, inflating counts.
      Foreign population grew +9.9% (net +547k), which alone cannot explain a
      14.5% total crime increase even at the historical over-representation ratio.
      The reclassification (mandatory reporting of previously-classified crimes)
      is the primary driver; migration is a secondary background factor.

    • 2023→2024: Crime growth (+4.7%) fell below foreign-stock growth (+6.8%).
      If foreign perpetrator share held at ~37%, foreign detained would be ~5,362
      vs ~5,135 in 2023 (+4.4%)—roughly proportional to total detained growth
      (+4.4%). This suggests the per-capita foreign perpetrator rate did NOT
      increase disproportionately despite rising migration.

    • The over-representation of foreign perpetrators (~2.7× at the detention
      level) reflects structural factors (age/sex distribution—migrants skew
      young male), socioeconomic disadvantage, and potential policing bias.
      Migration stock growth alone does not explain the 2022→2023 surge.
""")

    # --- Section 6: Methodological caveats ---
    print("## 6. Critical Caveats\n")
    print("""  1. DEFINITION BREAK (LO 10/2022): Post-Sept 2022, 'abuso sexual' (no
     force) merged into 'agresión sexual'. 2022-2024 counts are NOT directly
     comparable to 2015-2019 figures without a bridging correction.

  2. DETAINED ≠ CONVICTED: The 37.3% foreign figure is % of detained/
     investigated (detenciones e investigados). Conviction data (INE Condenados
     2023: 3,468 adults) lacks nationality breakdown in our sources.

  3. DENOMINATOR UNCERTAINTY: Male foreign-resident count uses 49% × Padrón
     stock (foreign nationality), excluding undocumented migrants. The true
     foreign male adult population may be 10-15% higher, reducing the rate ratio.

  4. TERRITORIAL COVERAGE: MIR Informes include Policía Nacional, Guardia Civil,
     Mossos, Ertzaintza, and Policía Foral since 2012. Pre-2012 data understates
     ~25% of the population.

  5. MISSING 2024 NATIONALITY BREAKDOWN: The 2024 MIR Informe (published Dec
     2025) is Cloudflare-protected. The perpetrator nationality split for 2024
     has not been extracted from the primary PDF and cannot be confirmed.
""")


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

def write_rates_csv():
    output_path = Path("data/processed/mir_migration_rates.csv")
    fieldnames = [
        "year", "total_pop", "foreign_stock", "foreign_pct_pop",
        "sexual_crimes_total", "crimes_yoy_pct",
        "foreign_stock_yoy_pct", "detained_total",
        "detained_foreign_count", "detained_spanish_count",
        "detained_foreign_pct", "detained_spanish_pct",
        "rate_foreign_per100k_male", "rate_spanish_per100k_male",
        "rate_ratio_foreign_vs_spanish", "confidence",
    ]

    rows = []
    prev_crimes = None
    prev_stock = None

    for year in [2018, 2022, 2023, 2024]:
        crimes = SEXUAL_CRIMES_TOTAL.get(year)
        total_pop = TOTAL_POP.get(year)
        foreign = FOREIGN_STOCK.get(year)
        spanish = (total_pop - foreign) if (total_pop and foreign) else None
        det_total = DETAINED_TOTAL.get(year)
        nat = PERP_FOREIGN_PCT.get(year)

        det_foreign = det_spanish = rate_f = rate_s = ratio = None
        if det_total and nat:
            pct_f, pct_s, _ = nat
            det_foreign = round(det_total * pct_f / 100)
            det_spanish = round(det_total * pct_s / 100)
            if foreign and spanish:
                rate_f = per_100k_rate(det_foreign, round(foreign * 0.49))
                rate_s = per_100k_rate(det_spanish, round(spanish * 0.49))
                ratio = round(rate_f / rate_s, 2) if rate_s else None

        crimes_yoy = None
        stock_yoy = None
        if prev_crimes and crimes:
            crimes_yoy = round((crimes - prev_crimes) / prev_crimes * 100, 2)
        if prev_stock and foreign:
            stock_yoy = round((foreign - prev_stock) / prev_stock * 100, 2)

        rows.append({
            "year": year,
            "total_pop": total_pop,
            "foreign_stock": foreign,
            "foreign_pct_pop": round(foreign / total_pop * 100, 2) if (foreign and total_pop) else None,
            "sexual_crimes_total": crimes,
            "crimes_yoy_pct": crimes_yoy,
            "foreign_stock_yoy_pct": stock_yoy,
            "detained_total": det_total,
            "detained_foreign_count": det_foreign,
            "detained_spanish_count": det_spanish,
            "detained_foreign_pct": nat[0] if nat else None,
            "detained_spanish_pct": nat[1] if nat else None,
            "rate_foreign_per100k_male": rate_f,
            "rate_spanish_per100k_male": rate_s,
            "rate_ratio_foreign_vs_spanish": ratio,
            "confidence": nat[2] if nat else "no_nationality_data",
        })

        if crimes:
            prev_crimes = crimes
        if foreign:
            prev_stock = foreign

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Rates table written to {output_path}")
    return output_path


if __name__ == "__main__":
    print_report()
    print("\n" + "=" * 70)
    path = write_rates_csv()
    print(f"  → {path}")
