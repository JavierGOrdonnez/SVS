"""T84 -- "over-corrected" denominator sensitivity scenario: how much would
Morocco/Algeria/Colombia/Venezuela's peligrosity rate fall if we assume the
ENTIRE 2026 regularization-application pool for that nationality (a) already
existed in Spain in every year of the crime-data window (2019-2024), just
uncounted in official population stock, (b) is 100% aged 15-59, and (c)
splits male/female in the same ratio as that nationality's already-
registered 15-59 population.

This is an explicit UPPER-BOUND scenario, not a best estimate -- the user's
own framing: "probably their reality is somewhere in the middle because not
all those people had arrived by 2024 nor were they absolutely all in the
15-59 age range." Two of its three assumptions push the correction as large
as it can plausibly go (all-working-age, present in every year including
the earliest); only the male/female split assumption is a genuinely
reasonable estimate (borrowed from that nationality's own real sex ratio).
Present this alongside, never instead of, the uncorrected rate (V14).

The regularization-application counts are held CONSTANT across all years
(added to each year's real, varying registered stock) -- we have no data on
when any given applicant arrived, so a constant hypothetical hidden
population is the simplest sensitivity bound, not a claim about actual
arrival timing.

Data sources:
  data/raw/regularization_2026.csv                  -- 2026 regularization
      application share by nationality (T-new, sourced from provisional
      press figures, see file's own source/notes columns)
  data/raw/migration_spain.csv (series=stock_nationality) -- real registered
      male/female 15-59 population by nationality x year (Eurostat)
  data/raw/sexual_crimes_mir_2017-2024.json          -- male perpetrator
      counts by country x year (MIR Informe, same extraction as
      analyze_cohort_crime_rate.py's load_perpetrator_counts())

Output:
  data/processed/regularization_sensitivity_test.csv
  data/processed/regularization_sensitivity.png (chart)
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
REG_CSV = ROOT / "data" / "raw" / "regularization_2026.csv"
MIGRATION_CSV = ROOT / "data" / "raw" / "migration_spain.csv"
MIR_JSON = ROOT / "data" / "raw" / "sexual_crimes_mir_2017-2024.json"
OUT_CSV = ROOT / "data" / "processed" / "regularization_sensitivity_test.csv"
OUT_CHART = ROOT / "data" / "processed" / "regularization_sensitivity.png"

COUNTRIES = {
    "MA": "MARRUECOS", "DZ": "ARGELIA", "CO": "COLOMBIA", "VE": "VENEZUELA",
    "PE": "PERU", "HN": "HONDURAS", "PY": "PARAGUAY", "SN": "SENEGAL",
    "PK": "PAKISTAN", "AR": "ARGENTINA",
}  # all 10 individually-named nationalities in data/raw/regularization_2026.csv
MIR_ALT_NAMES = {"VE": {"VENEZUELA", "VENUZUELA"}}  # spelling varies by report year
YEARS = [2019, 2021, 2022, 2023, 2024]
AGE_15_59 = {"15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59"}
REFERENCE_YEAR = 2024  # sex-split reference for allocating the (constant) added pool


def load_regularization_estimates():
    """{iso2: applications_estimated}"""
    out = {}
    with open(REG_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["iso2"] in COUNTRIES:
                out[r["iso2"]] = float(r["applications_estimated"])
    return out


def load_registered_stock():
    """{iso2: {year: {"male": n, "female": n}}}"""
    out = {c: {} for c in COUNTRIES}
    with open(MIGRATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["series"] != "stock_nationality" or r["country_of_origin"] not in COUNTRIES
                    or r["sex"] not in ("male", "female") or r["age_group"] not in AGE_15_59):
                continue
            year = int(r["year"])
            bucket = out[r["country_of_origin"]].setdefault(year, {"male": 0, "female": 0})
            bucket[r["sex"]] += int(r["value"])
    return out


def load_male_perpetrator_counts():
    """{iso2: {year: male_count}} -- same male-share backfill approach as
    analyze_cohort_crime_rate.py's load_perpetrator_counts() (2024 has no
    per-country sex breakdown in the source; approximate via that
    country's own historical male-share average)."""
    with open(MIR_JSON, encoding="utf-8") as f:
        data = json.load(f)
    name_to_iso2 = {}
    for iso2, name in COUNTRIES.items():
        name_to_iso2[name] = iso2
        for alt in MIR_ALT_NAMES.get(iso2, ()):
            name_to_iso2[alt] = iso2

    totals_by_iso2, male_by_iso2, report_male_pct = {}, {}, {}
    for report in data["reports"]:
        year = report["year"]
        if year not in YEARS:
            continue
        report_male_pct[year] = report.get("perp_male_pct")
        for e in report["nationality"]["perpetrators"]["by_country"]:
            iso2 = name_to_iso2.get(e["name"])
            if iso2 is None:
                continue
            totals_by_iso2.setdefault(iso2, {})[year] = e["total"]
            if e["male"] is not None:
                male_by_iso2.setdefault(iso2, {})[year] = e["male"]

    result = {}
    for iso2, totals in totals_by_iso2.items():
        known = male_by_iso2.get(iso2, {})
        if known:
            avg_male_share = sum(known[y] / totals[y] for y in known) / len(known)
        else:
            # No year has this country's own sex breakdown (e.g. a country
            # that only appears in MIR's top-N list for a year with no
            # per-country sex split at all) -- fall back to the report-
            # level (not nationality-specific) male share, same class of
            # approximation analyze_cohort_crime_rate.py's
            # load_spanish_perpetrator_counts() already uses.
            pcts = [p for p in report_male_pct.values() if p is not None]
            avg_male_share = (sum(pcts) / len(pcts) / 100) if pcts else 0.5
        result[iso2] = {
            y: (known[y] if y in known else round(t * avg_male_share))
            for y, t in totals.items()
        }
    return result


def main():
    reg = load_regularization_estimates()
    stock = load_registered_stock()
    perp = load_male_perpetrator_counts()

    rows = []
    for iso2, name in COUNTRIES.items():
        ref_male = stock[iso2][REFERENCE_YEAR]["male"]
        ref_female = stock[iso2][REFERENCE_YEAR]["female"]
        male_share = ref_male / (ref_male + ref_female)
        added_male_15_59 = reg[iso2] * male_share  # entire assumed pool is 15-59 (user's stated assumption)

        for year in YEARS:
            if year not in stock[iso2] or year not in perp.get(iso2, {}):
                continue
            original_denom = stock[iso2][year]["male"]
            corrected_denom = original_denom + added_male_15_59
            obs = perp[iso2][year]
            original_rate = obs / original_denom * 100000
            corrected_rate = obs / corrected_denom * 100000
            rows.append({
                "country": name, "iso2": iso2, "year": year,
                "observed_male_perpetrators": obs,
                "registered_male_15_59": original_denom,
                "regularization_applications_estimated": round(reg[iso2]),
                "male_share_used": round(male_share, 3),
                "added_male_15_59_upper_bound": round(added_male_15_59),
                "over_corrected_denom": round(original_denom + added_male_15_59),
                "denom_pct_increase": round(added_male_15_59 / original_denom * 100, 1),
                "original_rate_per_100k": round(original_rate, 1),
                "over_corrected_rate_per_100k": round(corrected_rate, 1),
                "rate_pct_reduction": round((original_rate - corrected_rate) / original_rate * 100, 1),
            })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")

    print("\n=== Male/female split used per nationality (from that country's own 2024 "
          f"registered 15-59 sex ratio, applied to its full regularization-application "
          f"count -- assumption (c) in the module docstring) ===")
    for iso2, name in COUNTRIES.items():
        m, fem = stock[iso2][REFERENCE_YEAR]["male"], stock[iso2][REFERENCE_YEAR]["female"]
        share = m / (m + fem)
        print(f"  {name:12} 2024 registered 15-59: male={m:>7} female={fem:>7}  "
              f"male_share={share*100:5.1f}%  regularization_est={reg[iso2]:>8.0f}  "
              f"-> added_male_15_59={reg[iso2]*share:>8.0f}")

    print("\n=== Upper-bound denominator sensitivity (assumes full 2026 regularization pool "
          "was already present, 100% aged 15-59, every year with MIR data) ===")
    for r in rows:
        print(f"  {r['country']:12} {r['year']}  obs={r['observed_male_perpetrators']:5}  "
              f"registered_denom={r['registered_male_15_59']:>7}  +{r['added_male_15_59_upper_bound']:>6} "
              f"({r['denom_pct_increase']:+.1f}%)  "
              f"rate {r['original_rate_per_100k']:>6.1f} -> {r['over_corrected_rate_per_100k']:>6.1f} "
              f"per 100k ({r['rate_pct_reduction']:+.1f}%)")

    make_chart(rows)


def make_chart(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    countries = list(dict.fromkeys(r["country"] for r in rows))
    ncols = 5
    nrows = -(-len(countries) // ncols)  # ceil
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows), sharey=False)
    axes_flat = axes.flat if hasattr(axes, "flat") else [axes]
    for ax, country in zip(axes_flat, countries):
        crows = [r for r in rows if r["country"] == country]
        years = [r["year"] for r in crows]
        x = range(len(years))
        w = 0.35
        ax.bar([i - w / 2 for i in x], [r["original_rate_per_100k"] for r in crows], w,
               label="Original (registered denom.)", color="#4C72B0")
        ax.bar([i + w / 2 for i in x], [r["over_corrected_rate_per_100k"] for r in crows], w,
               label="Over-corrected (upper-bound denom.)", color="#DD8452")
        ax.set_xticks(list(x))
        ax.set_xticklabels(years, fontsize=8)
        ax.set_title(country.title(), fontsize=10)
        ax.set_ylabel("Rate per 100k males", fontsize=8)
    for ax in axes_flat[len(countries):]:
        ax.axis("off")
    axes_flat[0].legend(loc="upper left", fontsize=7)
    fig.suptitle("Peligrosity rate: original vs. upper-bound over-corrected denominator\n"
                 "(assumes full 2026 regularization pool for that nationality was already present, all aged 15-59, every year with MIR data)")
    fig.tight_layout()
    fig.savefig(OUT_CHART, dpi=150)
    print(f"\nWrote chart -> {OUT_CHART}")


if __name__ == "__main__":
    main()
