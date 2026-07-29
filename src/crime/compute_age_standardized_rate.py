"""T77 -- indirect age-standardization test for the Morocco/Algeria peligrosity
divergence (H3): does Algeria's resident population skew younger than
Morocco's, and does that alone explain part of the gap in T41's raw
(unadjusted) rate ratios?

MIR's sexual-crime data has NO age x nationality cross (verified: the source
JSON schema -- categories/nationality.perpetrators.by_country -- carries no
age field at all), so a direct age-standardized numerator is not possible.
What IS possible is INDIRECT standardization (a standard epidemiological
technique for exactly this situation): build a reference age-specific
offending-RATE curve from a population where age and offending ARE crossed
(INE table 28857, T76 -- age x sex x nationality-REGION, but region-level
only, so DZ/MA cannot be isolated from 28857 itself), apply that reference
curve to each country's own age DISTRIBUTION (which IS available at
country level, from Eurostat's real age x sex x citizenship cross in
migration_spain.csv), and compare the resulting EXPECTED count (what the
country would show if it only differed from Spain's general population in
age composition) against its OBSERVED count. The ratio (observed/expected,
a standardized incidence ratio, SIR) isolates the age-composition
contribution from whatever remains.

Caveats (state prominently in any report using this output):
  - The reference curve is INE "condenados" (convicted) data; the observed
    counts being compared are MIR "identificados" (investigated/detained)
    data -- different funnel stages (V15's [convicted, identified]
    bracket), each with its own selection effects. This assumes the
    conviction-to-identification ratio is roughly age-invariant, which is
    NOT independently verified here.
  - The reference curve mixes ALL sexual-crime subtypes (28857 has no
    subtype breakdown) and reflects age AT CONVICTION, not age at offense
    (conviction lags offense by an unknown, possibly multi-year period,
    and historical-abuse convictions of older defendants for decades-old
    offenses would additionally bias the reference curve older).
  - Morocco/Algeria's population-by-age is only available in 5-year
    Eurostat bands, which do not align with INE 28857's own age bands
    (18-20/21-25/.../71+). Reallocating the 5-year bands into INE's bands
    assumes a UNIFORM population density within each 5-year band -- see
    REALLOC_MAP below. This approximation only affects the MA/DZ
    denominator side; the reference curve itself uses INE's own bands
    directly against EXACT single-year general population
    (population_spain_estimates.csv), no reallocation needed there.

Data sources:
  data/processed/ine_condenados_28857_age_nationality.csv -- reference
      age-specific conviction counts (T76, parse_ine_tabla28857.py)
  data/processed/population_spain_estimates.csv            -- single-year
      general population, used to build the reference age-specific RATE
      (exact, no reallocation)
  data/raw/migration_spain.csv (series=stock_nationality)   -- Morocco/
      Algeria age(5yr)x sex population cross (Eurostat migr_pop1ctz)
  data/raw/sexual_crimes_mir_2017-2024.json                 -- observed
      perpetrator counts by country (MIR Informe)

Output:
  data/processed/age_standardized_rate_test.csv
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
INE_28857_CSV = ROOT / "data" / "processed" / "ine_condenados_28857_age_nationality.csv"
POPULATION_CSV = ROOT / "data" / "processed" / "population_spain_estimates.csv"
MIGRATION_CSV = ROOT / "data" / "raw" / "migration_spain.csv"
MIR_JSON = ROOT / "data" / "raw" / "sexual_crimes_mir_2017-2024.json"
OUT_CSV = ROOT / "data" / "processed" / "age_standardized_rate_test.csv"
OUT_CSV_RATIO = ROOT / "data" / "processed" / "age_standardized_dz_ma_ratio.csv"

MIR_NAME = {"MA": "MARRUECOS", "DZ": "ARGELIA"}
MIR_YEARS = [2019, 2021, 2022, 2023, 2024]  # 2020 excluded, see B38 (unrelated to this test but same source)
INE_AGE_BANDS = ["18-20", "21-25", "26-30", "31-35", "36-40", "41-50", "51-60", "61-70", "71+"]

# INE age band -> [(eurostat 5yr band, fraction of that band's population
# falling in this INE band), ...], assuming uniform single-year population
# density within each Eurostat band. Only used for the MA/DZ side (the
# general reference population uses exact single-year ages instead).
REALLOC_MAP = {
    "18-20": [("15-19", 2 / 5), ("20-24", 1 / 5)],
    "21-25": [("20-24", 4 / 5), ("25-29", 1 / 5)],
    "26-30": [("25-29", 4 / 5), ("30-34", 1 / 5)],
    "31-35": [("30-34", 4 / 5), ("35-39", 1 / 5)],
    "36-40": [("35-39", 4 / 5), ("40-44", 1 / 5)],
    "41-50": [("40-44", 4 / 5), ("45-49", 1.0), ("50-54", 1 / 5)],
    "51-60": [("50-54", 4 / 5), ("55-59", 1.0), ("60-64", 1 / 5)],
    "61-70": [("60-64", 4 / 5), ("65-69", 1.0), ("70-74", 1 / 5)],
    "71+": [("70-74", 4 / 5), ("75-79", 1.0), ("80-84", 1.0), ("85+", 1.0)],
}


def load_reference_rate_curve(sex="male"):
    """{year: {ine_age_band: rate_per_person}} from INE 28857 (numerator,
    nationality=total) over exact single-year general population
    (denominator, population_spain_estimates.csv)."""
    convictions = {}
    with open(INE_28857_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["nationality"] != "total" or r["sex"] != sex or r["age"] == "total":
                continue
            year = int(r["year"])
            convictions.setdefault(year, {})[r["age"]] = int(r["count"])

    # Single-year population -> INE age bands (exact, no reallocation).
    band_bounds = {
        "18-20": (18, 20), "21-25": (21, 25), "26-30": (26, 30), "31-35": (31, 35),
        "36-40": (36, 40), "41-50": (41, 50), "51-60": (51, 60), "61-70": (61, 70),
        "71+": (71, 130),
    }
    pop_by_year_band = {}
    with open(POPULATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            # population_spain_estimates.csv carries INE's quarterly
            # reference dates (01-01/04-01/07-01/10-01) per year, un-
            # deduplicated -- match the mid-year convention already used
            # by population_spain_midyear_5yr.csv elsewhere in this repo,
            # or every quarter gets summed together (up to ~4x overcount).
            if r["sex"] != sex or not r["ref_date"].endswith("-07-01"):
                continue
            label = r["age_label"]
            if label == "100 y más años":
                age = 100
            elif label == "<1":
                age = 0
            else:
                digits = "".join(c for c in label if c.isdigit())
                if not digits:
                    continue
                age = int(digits)
            year = int(r["year"])
            for band, (lo, hi) in band_bounds.items():
                if lo <= age <= hi:
                    pop_by_year_band.setdefault(year, {}).setdefault(band, 0.0)
                    pop_by_year_band[year][band] += float(r["population"])
                    break

    rate_curve = {}
    for year in MIR_YEARS:
        if year not in convictions or year not in pop_by_year_band:
            continue
        rate_curve[year] = {}
        for band in INE_AGE_BANDS:
            c = convictions[year].get(band, 0)
            p = pop_by_year_band[year].get(band, 0)
            rate_curve[year][band] = c / p if p > 0 else 0.0
    return rate_curve


def load_country_age_population(code, sex="male"):
    """{year: {eurostat_5yr_band: population}} for MA/DZ from migration_spain.csv."""
    result = {}
    with open(MIGRATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["series"] != "stock_nationality" or r["country_of_origin"] != code
                    or r["sex"] != sex or r["age_group"] == "all"):
                continue
            year = int(r["year"])
            result.setdefault(year, {})[r["age_group"]] = int(r["value"])
    return result


def reallocate_to_ine_bands(pop_5yr):
    """{eurostat_5yr_band: pop} -> {ine_age_band: pop} via REALLOC_MAP."""
    out = {}
    for ine_band, parts in REALLOC_MAP.items():
        total = 0.0
        for eurostat_band, frac in parts:
            total += pop_5yr.get(eurostat_band, 0) * frac
        out[ine_band] = total
    return out


def load_observed_counts():
    """{mir_name: {year: male_count}} -- reuses the same MIR by_country
    perpetrator extraction as analyze_cohort_crime_rate.py's
    load_perpetrator_counts(), duplicated here per this repo's standalone-
    script convention (see SPEC.md §R -- scripts here intentionally don't
    cross-import). Male count where the report breaks it out; falls back
    to that country's own average male share across years it IS reported,
    same approximation load_perpetrator_counts() uses."""
    with open(MIR_JSON, encoding="utf-8") as f:
        data = json.load(f)
    totals_by_name, male_by_name = {}, {}
    for report in data["reports"]:
        year = report["year"]
        for entry in report["nationality"]["perpetrators"]["by_country"]:
            name = entry["name"]
            if name not in MIR_NAME.values():
                continue
            totals_by_name.setdefault(name, {})[year] = entry["total"]
            if entry["male"] is not None:
                male_by_name.setdefault(name, {})[year] = entry["male"]
    result = {}
    for name, totals in totals_by_name.items():
        known = male_by_name.get(name, {})
        avg_male_share = sum(known[y] / totals[y] for y in known) / len(known)
        result[name] = {
            y: (known[y] if y in known else round(t * avg_male_share))
            for y, t in totals.items()
        }
    return result


def poisson_ci(count, exposure, z=1.96):
    """Wald CI on a Poisson-rate ratio's observed/expected count -- exposure
    here is the EXPECTED count (already an estimate itself, see caveats in
    the module docstring), so this CI understates true uncertainty; do not
    present as exact."""
    if exposure <= 0:
        return None, None
    rate = count / exposure
    se_log = math.sqrt(1 / count) if count > 0 else float("inf")
    lo = rate * math.exp(-z * se_log) if count > 0 else 0.0
    hi = rate * math.exp(z * se_log) if count > 0 else None
    return lo, hi


def main():
    ref_curve_male = load_reference_rate_curve(sex="male")
    observed = load_observed_counts()

    rows = []
    for code, name in MIR_NAME.items():
        pop_5yr_by_year = load_country_age_population(code, sex="male")
        for year in MIR_YEARS:
            if year not in ref_curve_male or year not in pop_5yr_by_year:
                continue
            pop_ine_bands = reallocate_to_ine_bands(pop_5yr_by_year[year])
            expected = sum(
                ref_curve_male[year][band] * pop_ine_bands[band] for band in INE_AGE_BANDS
            )
            obs = observed.get(name, {}).get(year)
            if obs is None or expected <= 0:
                continue
            sir = obs / expected
            ci_lo, ci_hi = poisson_ci(obs, expected)
            total_male_pop = sum(pop_ine_bands.values())
            rows.append({
                "country": name, "code": code, "year": year,
                "observed_count": obs,
                "expected_count_age_standardized": round(expected, 1),
                "sir": round(sir, 3),
                "sir_ci_low": round(ci_lo, 3) if ci_lo is not None else "",
                "sir_ci_high": round(ci_hi, 3) if ci_hi is not None else "",
                "total_male_pop_15plus_approx": round(total_male_pop),
                "crude_rate_per_100k": round(obs / total_male_pop * 100000, 1) if total_male_pop > 0 else "",
                "note": "SIR=1 means the age-standardized reference rate fully explains the observed count; "
                        ">1 means an excess remains after adjusting for age composition alone",
            })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")

    print("\n=== Standardized Incidence Ratio (observed / age-standardized-expected) ===")
    for r in rows:
        ci = f"[{r['sir_ci_low']}, {r['sir_ci_high']}]" if r["sir_ci_low"] != "" else "n/a"
        print(f"  {r['country']:12} {r['year']}  obs={r['observed_count']:5}  "
              f"expected={r['expected_count_age_standardized']:8}  SIR={r['sir']:.2f}  "
              f"95% CI {ci}  crude_rate/100k={r['crude_rate_per_100k']}")

    # Algeria/Morocco SIR ratio vs crude-rate ratio, per year -- the
    # decision-relevant comparison for H3. Absolute SIR values are inflated
    # ~10-27x by the identified(MIR)-vs-convicted(INE) funnel-stage gap
    # (see module docstring), which is roughly SHARED between the two
    # countries and largely cancels when taking DZ/MA as a ratio; if age
    # composition explained part of the raw gap, the SIR ratio should sit
    # BELOW the crude rate ratio. If it doesn't, age composition is not
    # the explanation.
    by_year = {}
    for r in rows:
        by_year.setdefault(r["year"], {})[r["code"]] = r
    ratio_rows = []
    for year in sorted(by_year):
        pair = by_year[year]
        if "MA" not in pair or "DZ" not in pair:
            continue
        sir_ratio = pair["DZ"]["sir"] / pair["MA"]["sir"]
        crude_ratio = pair["DZ"]["crude_rate_per_100k"] / pair["MA"]["crude_rate_per_100k"]
        ratio_rows.append({
            "year": year,
            "sir_ratio_dz_over_ma": round(sir_ratio, 3),
            "crude_rate_ratio_dz_over_ma": round(crude_ratio, 3),
            "age_adjustment_effect": (
                "narrows gap" if sir_ratio < crude_ratio - 0.02
                else "widens gap" if sir_ratio > crude_ratio + 0.02
                else "no material change"
            ),
        })

    with open(OUT_CSV_RATIO, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ratio_rows[0].keys()))
        w.writeheader()
        w.writerows(ratio_rows)
    print(f"\nWrote {len(ratio_rows)} rows -> {OUT_CSV_RATIO}")

    print("\n=== Algeria/Morocco ratio: age-standardized (SIR) vs crude rate ===")
    for r in ratio_rows:
        print(f"  {r['year']}  SIR ratio={r['sir_ratio_dz_over_ma']:.2f}   "
              f"crude rate ratio={r['crude_rate_ratio_dz_over_ma']:.2f}   {r['age_adjustment_effect']}")


if __name__ == "__main__":
    main()
