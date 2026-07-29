#!/usr/bin/env python3
"""
T41 -- test whether the post-2022 arrival cohort of Moroccan/Algerian males
shows a sexual-crime perpetration rate statistically different from the
pre-surge established population (the "tenure-decay" null), and whether the
nationality group's overall rate shifted after the 2022 migration surge.

Two distinct, complementary hypothesis tests are run (both are two-sample
Poisson rate-ratio z-tests -- a normal-approximation score test to the exact
conditional-binomial test for comparing two Poisson rates with known
exposures; valid given the counts here are in the hundreds-to-thousands):

TEST A -- period-level (the direct "recent stock vs. original stock" test):
    compares the WHOLE nationality group's crime rate (count / total male
    15-59 stock) in each post-surge year (and pooled 2022-2024) against two
    baselines: the pre-2022 stock (pooled 2019+2021, the last pre-surge MIR
    report years) and the pre-2019 stock (2019 alone, the earliest available
    year). This uses only directly observed counts and stocks -- no cohort
    approximation. H0: rate_test == rate_baseline.

TEST B -- cohort-specific (the "is the NEW arrival sub-population itself
    elevated" test): MIR never splits perpetrator counts by tenure, so the
    total count is decomposed into a settled-population contribution (at a
    baseline rate estimated from Test A's pre-2022 baseline) plus a residual
    attributed to the recent-arrival cohort (per V25's cumulative-inflow
    approximation):
        crime(year) = r_settled_baseline * settled_pop(year) + r_cohort(year) * cohort_pop(year)
    This is necessarily noisier than Test A since it depends on the
    cohort/settled population split being a reasonable approximation.

TEST C -- share of total crimes (two-proportion z-test): whether the
    nationality group's share of ALL identified perpetrators (both sexes,
    since MIR's spanish_pct/foreign_pct split is not sex-specific) changed
    between baseline and test periods. Distinct from Test A: a group's rate
    can rise even while its SHARE falls (if the reference population's rate
    also rose), and vice versa -- this test isolates the share question
    directly. H0: share_test == share_baseline.

TEST D -- Test A's rate re-expressed per 100,000 males 15-59, for
    readability. Same statistic and p-values as Test A; presentational only.

TEST E -- is the group's rate INCREASE significantly different from the
    Spanish male population's rate increase over the same periods (a
    difference-in-differences / log-linear Poisson interaction z-test):
    ratio_of_ratios = (rate_group_test/rate_group_base) / (rate_spanish_test/rate_spanish_base).
    H0: ratio_of_ratios == 1. This needs a Spanish-specific male 15-59
    perpetrator count and population, neither of which is directly tabulated:
      - Spanish male perpetrator count: MIR's spanish_pct is reconstructed
        from foreign_total/foreign_pct (same method T42 uses), then
        multiplied by the report-level perp_male_pct (overall, not
        nationality-specific -- the same kind of approximation already used
        for the 2024 country-level male-share backfill in
        load_perpetrator_counts()).
      - Spanish male 15-59 population: migration_spain.csv has NO
        total-foreign-population-by-age-band across all nationalities (only
        MA/DZ have the real joint age x sex x citizenship cross, via T11/V25
        Eurostat). Approximated as total_male_15_59_pop - foreign_stock_total
        * (total_male_15_59_pop / total_all_pop), i.e. assuming the foreign
        population shares the general population's age/sex distribution.
        This likely UNDERSTATES the true foreign male-15-59 share (foreign
        residents, especially recent economic migrants, skew more
        male/working-age than the general population), so it OVERSTATES the
        Spanish denominator and UNDERSTATES the Spanish rate LEVEL in both
        periods -- but since the same bias direction applies at both
        baseline and test, its effect on the baseline-to-test RATE RATIO
        (the quantity Test E actually compares) is expected to largely
        cancel, so long as the foreign population's age/sex skew is roughly
        stable 2019-2024. Flagged explicitly; treat Test E as lower
        confidence than Tests A-C.

EXTENSION -- South America / EU-Europe (Test C only): the user asked to run
    the same comparison for South Americans and non-Spanish Europeans
    (EU/non-EU). Only Test C (share of total crimes) is computable for these
    groups -- Tests A/B/D/E all require a male-15-59 population/stock TIME
    SERIES, and migration_spain.csv has no such series for any country
    besides Morocco/Algeria (only MA/DZ went through the Eurostat
    migr_imm1ctz/migr_pop1ctz joint-cross extraction in
    parse_eurostat_migration_cohort.py). Other countries have at most a
    single 2025 stock snapshot -- unusable for a baseline-vs-test rate
    comparison. Two further group-definition caveats:
      - SOUTH AMERICA: MIR's own "AMERICA" region total conflates South
        America with Central America/Caribbean (Honduras, Dominican
        Republic appear as AMERICA siblings). So the group here is the SUM
        of individually-named South American countries (Colombia, Ecuador,
        Peru, Venezuela/Venuzuela, Bolivia, Paraguay, Argentina), not the
        region total. MIR only lists each year's top-N countries by count,
        so any South American country not making a given year's cutoff is
        folded into "RESTO"/"OTROS AMERICA" (not South-America-specific) and
        is NOT recovered -- this UNDERCOUNTS true South America, worse in
        earlier years (2019: 6 countries broken out; 2024: 8).
      - EU-EUROPE (excl. Spain): 2019-2023 MIR reports a clean "UNION
        EUROPEA" region total that is EU-only by construction (its own
        internal RESTO bucket is still EU) -- used directly, no undercount.
        2024 renamed the region "EUROPA (EXCEPTO ESPANA)" and started mixing
        in non-EU countries (Reino Unido, Ucrania) as flat siblings, so the
        2024 region total is no longer EU-only. 2024's EU figure is instead
        reconstructed by summing individually-named EU-member countries,
        which likely UNDERCOUNTS relative to 2019-2023 since it excludes
        "OTROS EUROPA" (may still contain EU nationals not in that year's
        top-10, e.g. Poland/Netherlands were named in earlier years but not
        2024) -- treat the 2024 EU figure as a soft break in comparability.
      - NON-EU EUROPE: NOT computable as a time series. Before 2024, MIR's
        "UNION EUROPEA" region excluded non-EU Europeans by construction, and
        they are not separately identifiable elsewhere -- they are inside
        "RESTO PAISES", an undifferentiated global residual mixed with every
        other unlisted nationality worldwide, not Europe-specific. Only 2024
        names non-EU European countries individually (Reino Unido, Ucrania),
        which is a single data point, not a baseline-to-test comparison.
        Skipped rather than fabricated.

H1 (null, all tests): no statistically detectable difference, consistent
    with tenure/assimilation literature.
H2: statistically significant difference (p < 0.05) in the hypothesized
    direction.

Association only -- no causal claim (V9). Test B's cohort_pop/settled_pop
split is an approximation per V25; all tests' baselines are estimated from
only 2 pre-surge MIR report years (2019, 2021 -- no report exists for 2020).

Data sources:
  data/raw/migration_spain.csv                       -- age x sex x
                                                          citizenship cross,
                                                          MA/DZ only (T11/V25,
                                                          Eurostat
                                                          migr_imm1ctz/migr_pop1ctz);
                                                          total foreign stock,
                                                          all nationalities
  data/raw/sexual_crimes_mir_2019-2024.json          -- per-country
                                                          perpetrator counts,
                                                          spanish/foreign
                                                          split, perp_male_pct
                                                          (T26)
  data/processed/population_spain_midyear_5yr.csv    -- general (all
                                                          nationality) mid-year
                                                          population by age x
                                                          sex

Output:
  data/processed/cohort_tenure_period_test.csv  -- Test A + D (period-level, incl. per-100k)
  data/processed/cohort_tenure_rates.csv        -- Test B (cohort-specific)
  data/processed/cohort_share_test.csv          -- Test C (share of total crimes)
  data/processed/cohort_vs_spanish_test.csv     -- Test E (vs Spanish population)
  data/processed/cohort_tenure_rate_ratio.png   -- all tests, grid (MA/DZ)
  data/processed/cohort_share_test_all_groups.png -- Test C, all groups incl.
                                                      South America/EU-Europe
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
MIGRATION_CSV = ROOT / "data" / "raw" / "migration_spain.csv"
MIR_JSON = ROOT / "data" / "raw" / "sexual_crimes_mir_2019-2024.json"
POPULATION_CSV = ROOT / "data" / "processed" / "population_spain_midyear_5yr.csv"
OUT_CSV_PERIOD = ROOT / "data" / "processed" / "cohort_tenure_period_test.csv"
OUT_CSV_COHORT = ROOT / "data" / "processed" / "cohort_tenure_rates.csv"
OUT_CSV_SHARE = ROOT / "data" / "processed" / "cohort_share_test.csv"
OUT_CSV_VS_SPANISH = ROOT / "data" / "processed" / "cohort_vs_spanish_test.csv"
OUT_CHART = ROOT / "data" / "processed" / "cohort_tenure_rate_ratio.png"
OUT_CHART_SHARE_ALL = ROOT / "data" / "processed" / "cohort_share_test_all_groups.png"

MIR_NAME = {"MA": "MARRUECOS", "DZ": "ARGELIA"}
# Extension groups (Test C only -- see module docstring "EXTENSION").
SOUTH_AMERICA_NAMES = {"COLOMBIA", "ECUADOR", "PERU", "VENEZUELA", "VENUZUELA",
                        "BOLIVIA", "PARAGUAY", "ARGENTINA"}
EU_EUROPE_NAMES = {"RUMANIA", "ALEMANIA", "ITALIA", "FRANCIA", "BULGARIA",
                    "PORTUGAL", "POLONIA", "BELGICA", "HOLANDA"}
COHORT_WINDOW_YEARS = 3          # trailing window incl. current year (V25)
BASELINE_PRE2022 = [2019, 2021]  # pooled pre-2022-surge MIR report years
BASELINE_PRE2019 = [2019]        # earliest available single MIR report year
TEST_YEARS = [2022, 2023, 2024]
AGE_BANDS_15_59 = {"15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59"}


def load_migration_totals():
    """Return {(country_code, 'flow'|'stock'): {year: male_15_59_total}}.

    B39 fix: the pre-fix version filtered series=="stock_foreign_nationality"
    (a name that no longer exists for MA/DZ post-T66 -- their stock rows are
    series=="stock_nationality") and did not restrict age_group to
    AGE_BANDS_15_59 despite the function's own docstring/dict-key naming,
    so it silently summed every age band (0-4 through 85+) rather than the
    working-age 15-59 band the rest of the module (load_population_totals)
    uses for the Spanish-population comparison. Both are fixed here; see
    SPEC.md B39 for the resulting change in Test A/B/D/E's published figures.
    """
    totals = {}
    with open(MIGRATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["country_of_origin"] not in MIR_NAME or r["sex"] != "male"
                    or r["age_group"] not in AGE_BANDS_15_59):
                continue
            if r["series"] == "flow_immigration_from_abroad":
                key = (r["country_of_origin"], "flow")
            elif r["series"] == "stock_nationality":
                key = (r["country_of_origin"], "stock")
            else:
                continue
            year = int(r["year"])
            bucket = totals.setdefault(key, {})
            bucket[year] = bucket.get(year, 0) + int(r["value"])
    return totals


def load_perpetrator_counts():
    """Return {mir_name: {year: (male_count, confidence)}}, backfilling years
    where MIR reports only a total with no sex breakdown (e.g. 2024) using
    that country's own historical male-share average."""
    with open(MIR_JSON, encoding="utf-8") as f:
        data = json.load(f)

    totals_by_name = {}
    male_by_name = {}
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
        by_year = {}
        for year, total in totals.items():
            if year in known:
                by_year[year] = (known[year], "high")
            else:
                by_year[year] = (round(total * avg_male_share), "medium")
        result[name] = by_year
    return result


def load_perpetrator_totals():
    """Return {mir_name: {year: total_count}} (both sexes, as directly
    reported -- no backfill needed since MIR always reports the total)."""
    with open(MIR_JSON, encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for report in data["reports"]:
        year = report["year"]
        for entry in report["nationality"]["perpetrators"]["by_country"]:
            name = entry["name"]
            if name not in MIR_NAME.values():
                continue
            result.setdefault(name, {})[year] = entry["total"]
    return result


def load_south_america_crime_totals():
    """{year: total perpetrator count (both sexes)} summed over individually-
    named South American countries -- NOT MIR's "AMERICA" region total, which
    also includes Central America/Caribbean. See module docstring EXTENSION
    for the resulting undercount caveat."""
    with open(MIR_JSON, encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for report in data["reports"]:
        year = report["year"]
        result[year] = sum(
            e["total"] for e in report["nationality"]["perpetrators"]["by_country"]
            if e["name"] in SOUTH_AMERICA_NAMES and not e.get("is_region_total"))
    return result


def load_eu_europe_crime_totals():
    """{year: total perpetrator count (both sexes)}, EU-Europe excl. Spain.
    2019-2023 uses MIR's own "UNION EUROPEA" region total directly (EU-only
    by construction). 2024 (renamed "EUROPA (EXCEPTO ESPANA)", now mixing in
    non-EU countries) is reconstructed by summing individually-named EU
    members instead. See module docstring EXTENSION for the caveat."""
    with open(MIR_JSON, encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for report in data["reports"]:
        year = report["year"]
        by_country = report["nationality"]["perpetrators"]["by_country"]
        region_total = next(
            (e["total"] for e in by_country
             if e.get("is_region_total") and e.get("region") == "UNION EUROPEA"), None)
        if region_total is not None:
            result[year] = region_total
        else:
            result[year] = sum(
                e["total"] for e in by_country
                if e["name"] in EU_EUROPE_NAMES and not e.get("is_region_total"))
    return result


def load_spanish_perpetrator_counts():
    """Return {year: {"spanish_male_count", "total_perp", "foreign_total"}}.
    total_perp/spanish_count are reconstructed the same way T42 does
    (foreign_total from summed by_country region totals, divided by
    foreign_pct); spanish_male_count then applies the report-level (not
    nationality-specific) perp_male_pct -- an approximation, see module
    docstring Test E."""
    with open(MIR_JSON, encoding="utf-8") as f:
        data = json.load(f)
    result = {}
    for report in data["reports"]:
        year = report["year"]
        perp = report["nationality"]["perpetrators"]
        foreign_total = sum(e["total"] for e in perp["by_country"] if e.get("is_region_total"))
        total_perp = foreign_total / (perp["foreign_pct"] / 100)
        spanish_count = total_perp - foreign_total
        spanish_male_count = spanish_count * report["perp_male_pct"] / 100
        result[year] = {
            "spanish_male_count": spanish_male_count,
            "total_perp": total_perp,
            "foreign_total": foreign_total,
        }
    return result


def load_population_totals():
    """Return ({year: male_15_59_pop}, {year: total_all_pop}) from the
    general (all-nationality) mid-year population estimates. No row carries
    age_group=='all' -- total_all is the sum across every age band for
    sex=='all'."""
    male_15_59, total_all = {}, {}
    with open(POPULATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            year = int(r["year"])
            pop = float(r["population_july1"])
            if r["sex"] == "male" and r["age_group"] in AGE_BANDS_15_59:
                male_15_59[year] = male_15_59.get(year, 0) + pop
            if r["sex"] == "all":
                total_all[year] = total_all.get(year, 0) + pop
    return male_15_59, total_all


def load_foreign_stock_total():
    """Return {year: total foreign-nationality stock, all ages, all sex,
    all countries of origin combined}."""
    stock = {}
    with open(MIGRATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["series"] == "stock_foreign_nationality" and r["country_of_origin"] == "all"
                    and r["nationality"] == "foreign" and r["age_group"] == "all" and r["sex"] == "all"):
                stock[int(r["year"])] = int(r["value"])
    return stock


def estimate_spanish_male_15_59(years):
    """Approximate Spanish-only male 15-59 population per year. See module
    docstring Test E for the approximation and its bias direction."""
    male_15_59, total_all = load_population_totals()
    foreign_stock = load_foreign_stock_total()
    result = {}
    for y in years:
        working_age_share = male_15_59[y] / total_all[y]
        foreign_male_15_59_est = foreign_stock[y] * working_age_share
        result[y] = male_15_59[y] - foreign_male_15_59_est
    return result


def poisson_var(count):
    return max(count, 0)


def poisson_rate_ratio_test(c_a, e_a, c_b, e_b):
    """Two-sample Poisson rate-ratio z-test (normal-approx score test to the
    exact conditional-binomial test). H0: rate_a == rate_b, i.e. c_b | c_a+c_b
    ~ Binomial(c_a+c_b, e_b/(e_a+e_b)). Returns None if undefined (n==0)."""
    n = c_a + c_b
    if n == 0 or e_a <= 0 or e_b <= 0:
        return None
    p_null = e_b / (e_a + e_b)
    expected_c_b = n * p_null
    var_c_b = n * p_null * (1 - p_null)
    if var_c_b <= 0:
        return None
    z = (c_b - expected_c_b) / math.sqrt(var_c_b)
    p_value = math.erfc(abs(z) / math.sqrt(2))
    rate_a, rate_b = c_a / e_a, c_b / e_b
    rate_ratio = rate_b / rate_a
    return {"rate_a": rate_a, "rate_b": rate_b, "rate_ratio": rate_ratio, "z": z, "p_value": p_value}


def classify(rate_ratio, p_value, alpha=0.05):
    if p_value is None:
        return "undefined"
    if p_value >= alpha:
        return "H1 (no significant difference)"
    return "H2 (significantly elevated)" if rate_ratio > 1 else "significantly below baseline"


def two_proportion_z_test(x_a, n_a, x_b, n_b):
    """Two-sample proportion z-test (pooled variance). H0: p_a == p_b.
    Used for Test C (share of total crimes)."""
    if n_a <= 0 or n_b <= 0:
        return None
    p_pool = (x_a + x_b) / (n_a + n_b)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se == 0:
        return None
    p_a, p_b = x_a / n_a, x_b / n_b
    z = (p_b - p_a) / se
    p_value = math.erfc(abs(z) / math.sqrt(2))
    return {"p_a": p_a, "p_b": p_b, "z": z, "p_value": p_value}


def classify_share(share_diff, p_value, alpha=0.05):
    if p_value is None:
        return "undefined"
    if p_value >= alpha:
        return "H1 (no significant change in share)"
    return "share significantly increased" if share_diff > 0 else "share significantly decreased"


def rate_ratio_of_rate_ratios_test(c_base_g, n_base_g, c_test_g, n_test_g,
                                    c_base_ref, n_base_ref, c_test_ref, n_test_ref):
    """Log-linear Poisson interaction (difference-in-differences) z-test:
    is the group's rate ratio (test/baseline) different from the reference
    population's rate ratio over the same periods? H0: ratio_of_ratios == 1.
    Exposures (n_*) are treated as known, as in poisson_rate_ratio_test."""
    if min(c_base_g, c_test_g, c_base_ref, c_test_ref) <= 0:
        return None
    log_rr_g = math.log(c_test_g / n_test_g) - math.log(c_base_g / n_base_g)
    var_g = 1 / c_test_g + 1 / c_base_g
    log_rr_ref = math.log(c_test_ref / n_test_ref) - math.log(c_base_ref / n_base_ref)
    var_ref = 1 / c_test_ref + 1 / c_base_ref
    diff = log_rr_g - log_rr_ref
    se = math.sqrt(var_g + var_ref)
    z = diff / se
    p_value = math.erfc(abs(z) / math.sqrt(2))
    return {
        "rr_group": math.exp(log_rr_g), "rr_reference": math.exp(log_rr_ref),
        "ratio_of_ratios": math.exp(diff), "z": z, "p_value": p_value,
    }


def classify_ror(ratio_of_ratios, p_value, alpha=0.05):
    if p_value is None:
        return "undefined"
    if p_value >= alpha:
        return "H1 (increase not significantly different from Spanish population)"
    return ("group increase significantly LARGER than Spanish" if ratio_of_ratios > 1
            else "group increase significantly SMALLER than Spanish")


def cohort_pop_for_year(flow_by_year, year):
    window = range(year - COHORT_WINDOW_YEARS + 1, year + 1)
    return sum(flow_by_year.get(y, 0) for y in window)


# ── Test A: period-level, whole nationality group, vs pre-2022 / pre-2019 ──

def run_test_a(group_name, code, stock_by_year, crime_by_year):
    rows = []
    baselines = {
        "pre_2022_pooled_2019_2021": BASELINE_PRE2022,
        "pre_2019_only": BASELINE_PRE2019,
    }
    test_windows = {str(y): [y] for y in TEST_YEARS}
    test_windows["pooled_2022_2024"] = TEST_YEARS

    for baseline_label, baseline_years in baselines.items():
        c_base = sum(crime_by_year[y][0] for y in baseline_years)
        e_base = sum(stock_by_year[y] for y in baseline_years)
        for test_label, test_yrs in test_windows.items():
            c_test = sum(crime_by_year[y][0] for y in test_yrs)
            e_test = sum(stock_by_year[y] for y in test_yrs)
            result = poisson_rate_ratio_test(c_base, e_base, c_test, e_test)
            if result is None:
                continue
            rows.append({
                "group": group_name, "country_code": code,
                "baseline": baseline_label, "test_period": test_label,
                "crime_baseline": c_base, "stock_baseline": e_base,
                "crime_test": c_test, "stock_test": e_test,
                "rate_baseline": result["rate_a"], "rate_test": result["rate_b"],
                # Test D: same statistic as Test A, per 100,000 males 15-59
                "rate_baseline_per_100k": result["rate_a"] * 100000,
                "rate_test_per_100k": result["rate_b"] * 100000,
                "rate_ratio": result["rate_ratio"], "z": result["z"], "p_value": result["p_value"],
                "hypothesis_call": classify(result["rate_ratio"], result["p_value"]),
            })
    return rows


# ── Test B: cohort-vs-settled residual decomposition (per-year) ───────────

def run_test_b(group_name, code, flow_by_year, stock_by_year, crime_by_year):
    years_needed = BASELINE_PRE2022 + TEST_YEARS
    cohort_by_year = {y: cohort_pop_for_year(flow_by_year, y) for y in years_needed}
    settled_by_year = {y: stock_by_year[y] - cohort_by_year[y] for y in years_needed}

    c_base = sum(crime_by_year[y][0] for y in BASELINE_PRE2022)
    n_base = sum(settled_by_year[y] for y in BASELINE_PRE2022)
    r_base = c_base / n_base
    var_r_base = poisson_var(c_base) / n_base ** 2

    rows = []
    for y in BASELINE_PRE2022:
        rows.append({
            "group": group_name, "country_code": code, "year": y, "role": "baseline",
            "crime_male": crime_by_year[y][0], "crime_confidence": crime_by_year[y][1],
            "settled_pop_male_15_59": settled_by_year[y],
            "cohort_pop_male_15_59": cohort_by_year[y],
            "cohort_window": f"{y - COHORT_WINDOW_YEARS + 1}-{y}",
            "r_settled_baseline": r_base,
            "r_cohort_implied": "", "rate_ratio": "", "z": "", "p_value": "",
            "hypothesis_call": "n/a (baseline year)",
        })

    for y in TEST_YEARS:
        c_year, conf = crime_by_year[y]
        s_year, p_year = settled_by_year[y], cohort_by_year[y]
        residual = c_year - r_base * s_year
        r_cohort = residual / p_year
        rate_ratio = r_cohort / r_base

        d_dC = 1 / (r_base * p_year)
        d_drbase = -c_year / (r_base ** 2 * p_year)
        var_ratio = (d_dC ** 2) * poisson_var(c_year) + (d_drbase ** 2) * var_r_base
        se = math.sqrt(var_ratio)
        z = (rate_ratio - 1) / se
        p_value = math.erfc(abs(z) / math.sqrt(2))

        rows.append({
            "group": group_name, "country_code": code, "year": y, "role": "test",
            "crime_male": c_year, "crime_confidence": conf,
            "settled_pop_male_15_59": s_year,
            "cohort_pop_male_15_59": p_year,
            "cohort_window": f"{y - COHORT_WINDOW_YEARS + 1}-{y}",
            "r_settled_baseline": r_base,
            "r_cohort_implied": r_cohort, "rate_ratio": rate_ratio, "z": z, "p_value": p_value,
            "hypothesis_call": classify(rate_ratio, p_value),
        })
    return rows


# ── Test C: share of total crimes, vs pre-2022 / pre-2019 ──────────────────

def run_test_c(group_name, code, crime_total_by_year, spanish_data):
    rows = []
    baselines = {
        "pre_2022_pooled_2019_2021": BASELINE_PRE2022,
        "pre_2019_only": BASELINE_PRE2019,
    }
    test_windows = {str(y): [y] for y in TEST_YEARS}
    test_windows["pooled_2022_2024"] = TEST_YEARS

    for baseline_label, baseline_years in baselines.items():
        x_base = sum(crime_total_by_year[y] for y in baseline_years)
        n_base = sum(spanish_data[y]["total_perp"] for y in baseline_years)
        for test_label, test_yrs in test_windows.items():
            x_test = sum(crime_total_by_year[y] for y in test_yrs)
            n_test = sum(spanish_data[y]["total_perp"] for y in test_yrs)
            result = two_proportion_z_test(x_base, n_base, x_test, n_test)
            if result is None:
                continue
            rows.append({
                "group": group_name, "country_code": code,
                "baseline": baseline_label, "test_period": test_label,
                "crimes_baseline": x_base, "total_perp_baseline": round(n_base),
                "crimes_test": x_test, "total_perp_test": round(n_test),
                "share_baseline_pct": result["p_a"] * 100, "share_test_pct": result["p_b"] * 100,
                "z": result["z"], "p_value": result["p_value"],
                "hypothesis_call": classify_share(result["p_b"] - result["p_a"], result["p_value"]),
            })
    return rows


# ── Test E: group rate-increase vs Spanish male-population rate-increase ───

def run_test_e(group_name, code, stock_by_year, crime_by_year, spanish_male_pop, spanish_data):
    rows = []
    baselines = {
        "pre_2022_pooled_2019_2021": BASELINE_PRE2022,
        "pre_2019_only": BASELINE_PRE2019,
    }
    test_windows = {str(y): [y] for y in TEST_YEARS}
    test_windows["pooled_2022_2024"] = TEST_YEARS

    for baseline_label, baseline_years in baselines.items():
        c_base_g = sum(crime_by_year[y][0] for y in baseline_years)
        n_base_g = sum(stock_by_year[y] for y in baseline_years)
        c_base_es = sum(spanish_data[y]["spanish_male_count"] for y in baseline_years)
        n_base_es = sum(spanish_male_pop[y] for y in baseline_years)
        for test_label, test_yrs in test_windows.items():
            c_test_g = sum(crime_by_year[y][0] for y in test_yrs)
            n_test_g = sum(stock_by_year[y] for y in test_yrs)
            c_test_es = sum(spanish_data[y]["spanish_male_count"] for y in test_yrs)
            n_test_es = sum(spanish_male_pop[y] for y in test_yrs)
            result = rate_ratio_of_rate_ratios_test(
                c_base_g, n_base_g, c_test_g, n_test_g,
                c_base_es, n_base_es, c_test_es, n_test_es)
            if result is None:
                continue
            rows.append({
                "group": group_name, "country_code": code,
                "baseline": baseline_label, "test_period": test_label,
                "group_rate_ratio": result["rr_group"], "spanish_rate_ratio": result["rr_reference"],
                "ratio_of_ratios": result["ratio_of_ratios"],
                "z": result["z"], "p_value": result["p_value"],
                "hypothesis_call": classify_ror(result["ratio_of_ratios"], result["p_value"]),
            })
    return rows


def main():
    migration = load_migration_totals()
    crimes = load_perpetrator_counts()
    crime_totals = load_perpetrator_totals()
    spanish_data = load_spanish_perpetrator_counts()
    all_years = sorted(set(BASELINE_PRE2022) | set(BASELINE_PRE2019) | set(TEST_YEARS))
    spanish_male_pop = estimate_spanish_male_15_59(all_years)

    per_group = {}
    for code, name in MIR_NAME.items():
        per_group[code] = {
            "name": name,
            "flow": migration[(code, "flow")],
            "stock": migration[(code, "stock")],
            "crime": crimes[name],
            "crime_total": crime_totals[name],
        }

    combined_flow, combined_stock, combined_crime, combined_crime_total = {}, {}, {}, {}
    for code in MIR_NAME:
        g = per_group[code]
        for y, v in g["flow"].items():
            combined_flow[y] = combined_flow.get(y, 0) + v
        for y, v in g["stock"].items():
            combined_stock[y] = combined_stock.get(y, 0) + v
        for y, (m, conf) in g["crime"].items():
            prev_m, prev_conf = combined_crime.get(y, (0, "high"))
            worse_conf = conf if conf != "high" else prev_conf
            combined_crime[y] = (prev_m + m, worse_conf)
        for y, v in g["crime_total"].items():
            combined_crime_total[y] = combined_crime_total.get(y, 0) + v
    per_group["MA+DZ"] = {"name": "MARRUECOS+ARGELIA", "flow": combined_flow,
                           "stock": combined_stock, "crime": combined_crime,
                           "crime_total": combined_crime_total}

    rows_a, rows_b, rows_c, rows_e = [], [], [], []
    for code, g in per_group.items():
        rows_a += run_test_a(g["name"], code, g["stock"], g["crime"])
        rows_b += run_test_b(g["name"], code, g["flow"], g["stock"], g["crime"])
        rows_c += run_test_c(g["name"], code, g["crime_total"], spanish_data)
        rows_e += run_test_e(g["name"], code, g["stock"], g["crime"], spanish_male_pop, spanish_data)

    # Extension: South America / EU-Europe -- Test C only, no stock/flow time
    # series exists for these groups (see module docstring EXTENSION).
    sa_crime_total = load_south_america_crime_totals()
    eu_crime_total = load_eu_europe_crime_totals()
    rows_c += run_test_c("SOUTH AMERICA (named countries)", "SA", sa_crime_total, spanish_data)
    rows_c += run_test_c("EU EUROPE excl. Spain", "EU", eu_crime_total, spanish_data)

    OUT_CSV_PERIOD.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV_PERIOD, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_a[0].keys()))
        w.writeheader()
        w.writerows(rows_a)
    print(f"Wrote {len(rows_a)} rows -> {OUT_CSV_PERIOD}")

    with open(OUT_CSV_COHORT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_b[0].keys()))
        w.writeheader()
        w.writerows(rows_b)
    print(f"Wrote {len(rows_b)} rows -> {OUT_CSV_COHORT}")

    with open(OUT_CSV_SHARE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_c[0].keys()))
        w.writeheader()
        w.writerows(rows_c)
    print(f"Wrote {len(rows_c)} rows -> {OUT_CSV_SHARE}")

    with open(OUT_CSV_VS_SPANISH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_e[0].keys()))
        w.writeheader()
        w.writerows(rows_e)
    print(f"Wrote {len(rows_e)} rows -> {OUT_CSV_VS_SPANISH}")

    print("\nTEST A -- period-level (whole nationality group, recent stock vs original stock):")
    for r in rows_a:
        print(f"  {r['group']:20} {r['baseline']:26} vs {r['test_period']:16} "
              f"rate_ratio={r['rate_ratio']:.2f}  z={r['z']:+.2f}  p={r['p_value']:.4f}  {r['hypothesis_call']}")

    print("\nTEST B -- cohort-specific (recent-arrival cohort vs settled sub-population):")
    for r in rows_b:
        if r["role"] == "test":
            print(f"  {r['group']:20} {r['year']}  rate_ratio={r['rate_ratio']:.2f}  "
                  f"z={r['z']:+.2f}  p={r['p_value']:.4f}  {r['hypothesis_call']}")

    print("\nTEST C -- share of total identified perpetrators (both sexes):")
    for r in rows_c:
        print(f"  {r['group']:20} {r['baseline']:26} vs {r['test_period']:16} "
              f"share {r['share_baseline_pct']:.2f}% -> {r['share_test_pct']:.2f}%  "
              f"z={r['z']:+.2f}  p={r['p_value']:.4f}  {r['hypothesis_call']}")

    print("\nTEST E -- group rate-ratio vs Spanish male-population rate-ratio (diff-in-diff):")
    for r in rows_e:
        print(f"  {r['group']:20} {r['baseline']:26} vs {r['test_period']:16} "
              f"group_RR={r['group_rate_ratio']:.2f}  spanish_RR={r['spanish_rate_ratio']:.2f}  "
              f"ratio_of_ratios={r['ratio_of_ratios']:.2f}  z={r['z']:+.2f}  p={r['p_value']:.4f}  {r['hypothesis_call']}")

    make_chart(rows_a, rows_b, rows_c, rows_e)
    make_share_chart_all_groups(rows_c)


def make_chart(rows_a, rows_b, rows_c, rows_e):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = ["MARRUECOS", "ARGELIA", "MARRUECOS+ARGELIA"]

    fig, axes = plt.subplots(4, 3, figsize=(14, 17), sharey="row")

    # Row 1: Test A -- pre-2022 baseline vs each test year + pooled
    for ax, g in zip(axes[0], groups):
        rs = [r for r in rows_a if r["group"] == g and r["baseline"] == "pre_2022_pooled_2019_2021"
              and r["test_period"] != "pooled_2022_2024"]
        years = [int(r["test_period"]) for r in rs]
        ratios = [r["rate_ratio"] for r in rs]
        colors = ["tab:red" if r["p_value"] < 0.05 else "tab:blue" for r in rs]
        ax.scatter(years, ratios, c=colors, s=60, zorder=3)
        for r, y in zip(rs, years):
            ax.annotate(f"p={r['p_value']:.3f}", (y, r["rate_ratio"]), fontsize=7,
                        textcoords="offset points", xytext=(5, 5))
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_title(f"Test A: {g}\n(vs pre-2022 stock)")
        ax.set_xlabel("year")
        ax.set_xticks(years)
    axes[0][0].set_ylabel("rate ratio (test year / pre-2022 baseline)\nred = p<0.05")

    # Row 2: Test B -- cohort vs settled residual, with p-value coloring
    test_rows = {g: [r for r in rows_b if r["group"] == g and r["role"] == "test"] for g in groups}
    for ax, g in zip(axes[1], groups):
        rs = test_rows[g]
        years = [r["year"] for r in rs]
        ratios = [r["rate_ratio"] for r in rs]
        colors = ["tab:red" if r["p_value"] < 0.05 else "tab:blue" for r in rs]
        ax.scatter(years, ratios, c=colors, s=60, zorder=3)
        for r, y in zip(rs, years):
            ax.annotate(f"p={r['p_value']:.3f}", (y, r["rate_ratio"]), fontsize=7,
                        textcoords="offset points", xytext=(5, 5))
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_title(f"Test B: {g}\n(implied cohort vs settled)")
        ax.set_xlabel("year")
        ax.set_xticks(years)
    axes[1][0].set_ylabel("rate ratio (implied cohort / settled baseline)\nred = p<0.05")

    # Row 3: Test C -- share of total identified perpetrators, pre-2022 baseline
    for ax, g in zip(axes[2], groups):
        rs = [r for r in rows_c if r["group"] == g and r["baseline"] == "pre_2022_pooled_2019_2021"
              and r["test_period"] != "pooled_2022_2024"]
        years = [int(r["test_period"]) for r in rs]
        shares = [r["share_test_pct"] for r in rs]
        colors = ["tab:red" if r["p_value"] < 0.05 else "tab:blue" for r in rs]
        ax.scatter(years, shares, c=colors, s=60, zorder=3)
        for r, y in zip(rs, years):
            ax.annotate(f"p={r['p_value']:.3f}", (y, r["share_test_pct"]), fontsize=7,
                        textcoords="offset points", xytext=(5, 5))
        baseline_share = rs[0]["share_baseline_pct"] if rs else None
        if baseline_share is not None:
            ax.axhline(baseline_share, color="gray", linestyle="--", linewidth=1)
        ax.set_title(f"Test C: {g}\n(share of total perpetrators)")
        ax.set_xlabel("year")
        ax.set_xticks(years)
    axes[2][0].set_ylabel("share of total identified perpetrators (%)\ndashed = pre-2022 baseline share; red = p<0.05")

    # Row 4: Test E -- ratio of rate ratios vs Spanish male population
    for ax, g in zip(axes[3], groups):
        rs = [r for r in rows_e if r["group"] == g and r["baseline"] == "pre_2022_pooled_2019_2021"
              and r["test_period"] != "pooled_2022_2024"]
        years = [int(r["test_period"]) for r in rs]
        ratios = [r["ratio_of_ratios"] for r in rs]
        colors = ["tab:red" if r["p_value"] < 0.05 else "tab:blue" for r in rs]
        ax.scatter(years, ratios, c=colors, s=60, zorder=3)
        for r, y in zip(rs, years):
            ax.annotate(f"p={r['p_value']:.3f}", (y, r["ratio_of_ratios"]), fontsize=7,
                        textcoords="offset points", xytext=(5, 5))
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_title(f"Test E: {g}\n(vs Spanish male pop. rate-ratio)")
        ax.set_xlabel("year")
        ax.set_xticks(years)
    axes[3][0].set_ylabel("ratio of rate-ratios (group / Spanish)\nred = p<0.05")

    fig.suptitle("T41 -- sexual-crime rate-ratio hypothesis tests (Poisson two-sample z-test)\n"
                 "association only, not causal; red = statistically significant at alpha=0.05")
    fig.tight_layout()
    fig.savefig(OUT_CHART, dpi=150)
    print(f"\nWrote chart -> {OUT_CHART}")


def make_share_chart_all_groups(rows_c):
    """Test C (share of total identified perpetrators) across every group,
    including the South America / EU-Europe extension groups that have no
    Test A/B/D/E data (no population time series -- see module docstring
    EXTENSION)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = ["MARRUECOS", "ARGELIA", "MARRUECOS+ARGELIA",
              "SOUTH AMERICA (named countries)", "EU EUROPE excl. Spain"]

    fig, axes = plt.subplots(1, len(groups), figsize=(20, 4.5), sharey=True)
    for ax, g in zip(axes, groups):
        rs = [r for r in rows_c if r["group"] == g and r["baseline"] == "pre_2022_pooled_2019_2021"
              and r["test_period"] != "pooled_2022_2024"]
        years = [int(r["test_period"]) for r in rs]
        shares = [r["share_test_pct"] for r in rs]
        colors = ["tab:red" if r["p_value"] < 0.05 else "tab:blue" for r in rs]
        ax.scatter(years, shares, c=colors, s=60, zorder=3)
        for r, y in zip(rs, years):
            ax.annotate(f"p={r['p_value']:.3f}", (y, r["share_test_pct"]), fontsize=7,
                        textcoords="offset points", xytext=(5, 5))
        baseline_share = rs[0]["share_baseline_pct"] if rs else None
        if baseline_share is not None:
            ax.axhline(baseline_share, color="gray", linestyle="--", linewidth=1)
        ax.set_title(g, fontsize=9)
        ax.set_xlabel("year")
        ax.set_xticks(years)
    axes[0].set_ylabel("share of total identified perpetrators (%)\ndashed = pre-2022 baseline share; red = p<0.05")

    fig.suptitle("Test C -- share of total perpetrators, all groups (incl. South America / EU-Europe extension)\n"
                 "association only, not causal; South America/EU-Europe have Test C only, no population time series")
    fig.tight_layout()
    fig.savefig(OUT_CHART_SHARE_ALL, dpi=150)
    print(f"Wrote chart -> {OUT_CHART_SHARE_ALL}")


if __name__ == "__main__":
    main()
