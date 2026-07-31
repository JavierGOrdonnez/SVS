#!/usr/bin/env python3
"""
T41 -- test whether the post-2022 arrival cohort of Moroccan/Algerian males
shows a sexual-crime perpetration rate statistically different from the
pre-surge established population (the "tenure-decay" null), and whether the
nationality group's overall rate shifted after the 2022 migration surge.

Five distinct, complementary hypothesis tests are run (Tests A/D/E are
two-sample Poisson rate-ratio z-tests -- a normal-approximation score test to
the exact conditional-binomial test for comparing two Poisson rates with
known exposures; valid given the counts here are in the hundreds-to-thousands):

TEST A -- period-level (the direct "recent stock vs. original stock" test):
    compares the WHOLE nationality group's crime rate (count / total male
    15-59 stock) in each post-surge year (and pooled 2022-2024) against
    THREE baselines: the pre-2022 stock (pooled 2019+2021), the pre-2019
    stock (2019 alone), and a deeper pre-2020 stock (pooled 2017-2019,
    added B42 -- see below). This uses only directly observed counts and
    stocks -- no cohort approximation. H0: rate_test == rate_baseline.

TEST B -- cohort-specific (the "is the NEW arrival sub-population itself
    elevated" test): MIR never splits perpetrator counts by tenure, so the
    total count is decomposed into a settled-population contribution (at a
    baseline rate estimated from the group's own pre-surge total rate) plus
    a residual attributed to the recent-arrival cohort:
        crime(year) = r_settled_baseline * settled_pop(year) + r_cohort(year) * cohort_pop(year)
    This is necessarily noisier than Test A since it depends on the
    cohort/settled population split being a reasonable approximation.

    CORRECTION (B42, 2026-07-30): the original implementation had two
    compounding design flaws, found while re-examining this test at a user's
    request:
      (1) cohort_pop was approximated as a trailing-3yr sum of GROSS
          immigration inflow (series flow_immigration_from_abroad), never
          netted against emigration (no such data exists in this repo --
          see V25/N3). This produced an implausibly COLLAPSING implied
          settled population over time (Algeria: 18,017 -> 6,382 from 2019
          to 2024, a 65% "decline" in a population that was actually
          growing) and, for Algeria specifically, cohort_pop approaching the
          ENTIRE stock (83% of 2024 stock), making the decomposition
          numerically degenerate exactly where the interesting question
          lives.
      (2) r_settled_baseline was computed as TOTAL baseline crime (both
          settled+cohort) divided by the SETTLED-ONLY baseline population.
          This is not an estimate of anything -- algebraically,
          r_base = c_base/n_settled = (c_base/n_total)*(n_total/n_settled)
          = total_rate / settled_share, a deterministic rescaling of the
          total rate that is exactly what you'd get if cohort and settled
          sub-populations had IDENTICAL rates at baseline. It assumed away
          the very question Test B claims to test, and inflated r_base in
          proportion to how large (and, per flaw 1, artificially inflated)
          the cohort population was estimated to be.
    Both are fixed:
      (1) cohort_pop is now a NET-STOCK-DELTA: cohort_pop(year) =
          stock(year) - stock(year - window); settled_pop(year) =
          stock(year - window) directly. Both terms come from the SAME
          `stock_nationality` series (no separate flow series with a
          different definition/coverage), settled_pop is bounded and
          well-behaved by construction (a real historical stock value, not
          a residual that can implode), and it needs no emigration data --
          stock is already a net quantity. Remaining caveat: any churn
          within the pre-existing settled sub-population during the window
          (naturalization, death, re-emigration) is silently absorbed into
          the net delta, which can understate true recent-arrival volume --
          a much smaller, standard demographic approximation than flaw (1)
          and requires no new data.
      (2) r_settled_baseline is now anchored to the group's own TOTAL
          baseline rate (crime_baseline / stock_baseline, identical to Test
          A's rate_baseline for the same baseline years) rather than a
          settled-only-denominator reconstruction. H0 is now coherent: "if
          nothing changed, both the settled AND cohort sub-populations would
          still show the pre-surge OVERALL rate" -- and Test B asks whether
          the observed total, once the settled sub-population's expected
          contribution at that rate is subtracted, leaves a cohort residual
          rate different from that same baseline rate.
    Test B is now also run against a NEW, deeper baseline (pre_2020_pooled
    _2017_2019, see Test A) alongside the original pre_2022 baseline, and
    against a regularization-adjusted sensitivity variant (see EXTENSION
    below) -- all tagged by a `baseline` column so old and new results are
    directly comparable in the same CSV.

    CORRECTION (B43, 2026-07-30): B42's fix left the ratio implausibly large
    (4x-6x) because it still assumed the settled sub-population's rate stays
    completely FROZEN at the pre-surge baseline in every test year -- but
    Test E independently shows the reference Spanish population's own rate
    rose 11%-34% over the same span, a broad, non-migration-specific rise.
    Freezing settled at the old level while all of Spanish society moved on
    forced the ENTIRE societal-wide rise onto the tiny cohort bucket on top
    of any real cohort-specific effect. Fixed: the settled baseline rate is
    now scaled by the same trend observed in the Spanish reference
    population between baseline and test year (r_expected_settled = r_base *
    spanish_trend), so the cohort residual is the excess above what a
    society-wide (not cohort-specific) rise would already predict for the
    settled sub-population -- see run_test_b()'s docstring for the exact
    derivation. This shrinks the ratio substantially (though it remains
    elevated for both countries in most years).

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
    Spanish male population's rate INCREASE over the same periods (a
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

EXTENSION -- regularization-adjusted sensitivity (Test B only, T85-style):
    Test B's settled/cohort split is entirely blind to undocumented
    migrants -- MIR/Eurostat stock only counts REGISTERED residents. Spain's
    2026 extraordinary regularization process surfaced applicants whose only
    stated eligibility bar was residence before 2026-01-01 -- consistent with
    EITHER long tenure OR recent arrival, since ordinary multi-year
    residency-based channels (arraigo social/laboral, requiring 2-3 years'
    continuous residency) already exist for anyone long-settled; people still
    undocumented despite years in Spain would mostly have had a chance to
    regularize through those instead. CORRECTION (B43, 2026-07-30): the
    original version (B42) assumed the opposite -- that this hidden
    population was long-settled -- and added it to settled_pop. Revised: the
    hidden population is now assumed RECENT (the more defensible read of why
    an extraordinary, lower-bar amnesty was needed at all) and added to
    cohort_pop instead. Mirrors T85's three assumptions exactly: (a) the
    entire regularization-application pool for that nationality was already
    present throughout the whole 2019-2024 crime-data window, just
    uncounted, (b) 100% aged 15-59, (c) split male/female per that
    nationality's own real 2024 registered 15-59 sex ratio; held CONSTANT
    across every year (baseline and test alike), matching T85's own "no
    arrival-timing data, so hold constant" convention -- association only,
    we have no true arrival-year data for applicants, so this is the more
    defensible of the two buckets to place them in, not a claim about actual
    tenure. This is an explicit UPPER BOUND, not a best estimate (V14);
    present alongside, never instead of, the unadjusted result.

TEST F -- fixed-cutoff cohort/settled split (added 2026-07-30, per user
    request): Test B's rolling 3-year window redefines "recent arrival"
    relative to every observation year, which doesn't literally match the
    original framing of this whole investigation ("modern stock vs the
    pre-2020/2022 population"). Test F instead uses a single, fixed
    calendar cutoff: settled_pop is pinned ONCE at stock(cutoff_year - 1)
    and held fixed for every test year at/after the cutoff (not recomputed
    per year); cohort_pop = stock(year) - settled_pop. Run for two cutoffs:
      - cutoff=2022: "arrived 2022 onward" vs "everyone here before 2022"
        (test years 2022, 2023, 2024 -- cohort_pop grows each year as more
        time accumulates since the cutoff).
      - cutoff=2024: "arrived 2024 onward" vs "everyone here before 2024"
        (test year 2024 only -- the narrowest, most literal "just the
        newest arrivals" comparison, with the deepest possible baseline,
        since everything through 2023 counts as "before").
    The baseline rate is estimated from EVERY available real MIR year
    strictly before that specific cutoff (not a fixed 2-3-year pooled set
    as in Test B) -- deeper for cutoff=2024 (2017-2023, 2020 excluded per
    B38) than for cutoff=2022 (2017-2019+2021). Settled's expected rate is
    trend-adjusted against the Spanish reference population exactly as in
    Test B (same reasoning: don't let the whole of Spanish society's own
    documented rate rise get misattributed to the tiny cohort bucket).
    Also run with a regularization-adjusted variant: the 2026
    regularization-application pool is assumed to have arrived at/after
    whichever cutoff is being tested (added to cohort_pop, same reasoning
    as Test B's B43 correction) -- explicit upper bound, not a best
    estimate (V14).

South America / EU-Europe (Test C only): the user asked to run the same
    comparison for South Americans and non-Spanish Europeans (EU/non-EU).
    Only Test C (share of total crimes) is computable for these groups --
    Tests A/B/D/E all require a male-15-59 population/stock TIME SERIES, and
    migration_spain.csv has no such series for any country besides
    Morocco/Algeria (only MA/DZ went through the Eurostat
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
split is an approximation per V25 (updated B42); all tests' baselines are
estimated from real MIR report years only (2020 excluded throughout --
corrupted victim-side data per B38, perpetrator-side is fine but excluded
for consistency; no report exists covering any other gap year).

Data sources:
  data/raw/migration_spain.csv                       -- age x sex x
                                                          citizenship cross,
                                                          MA/DZ only (T11/V25,
                                                          Eurostat
                                                          migr_imm1ctz/migr_pop1ctz);
                                                          total foreign stock,
                                                          all nationalities
  data/raw/sexual_crimes_mir_2017-2024.json          -- per-country
                                                          perpetrator counts,
                                                          spanish/foreign
                                                          split, perp_male_pct
                                                          (T26, extended to
                                                          2017-2018 by T83/T87)
  data/processed/population_spain_midyear_5yr.csv    -- general (all
                                                          nationality) mid-year
                                                          population by age x
                                                          sex
  data/raw/regularization_2026.csv                   -- 2026 regularization
                                                          application share by
                                                          nationality (N20/T85)

Output:
  data/processed/cohort_tenure_period_test.csv        -- Test A + D (period-level, incl. per-100k)
  data/processed/cohort_tenure_rates.csv               -- Test B (cohort-specific, both baselines)
  data/processed/cohort_tenure_regularization_sensitivity.csv -- Test B, regularization-adjusted (B42/T85)
  data/processed/cohort_share_test.csv                 -- Test C (share of total crimes)
  data/processed/cohort_vs_spanish_test.csv            -- Test E (vs Spanish population)
  data/processed/cohort_tenure_rate_ratio.png          -- all tests, grid (MA/DZ)
  data/processed/cohort_tenure_regularization_sensitivity.png -- Test B sensitivity chart
  data/processed/cohort_tenure_fixed_cutoff_test.csv   -- Test F (fixed-cutoff, both cutoffs)
  data/processed/cohort_tenure_fixed_cutoff_regularization_sensitivity.csv -- Test F, regularization-adjusted
  data/processed/cohort_tenure_fixed_cutoff_test.png   -- Test F chart
  data/processed/cohort_share_test_all_groups.png      -- Test C, all groups incl.
                                                          South America/EU-Europe
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
MIGRATION_CSV = ROOT / "data" / "raw" / "migration_spain.csv"
POPULATION_NATIONALITY_CSV = ROOT / "data" / "processed" / "population_spain_nationality.csv"
MIR_JSON = ROOT / "data" / "raw" / "sexual_crimes_mir_2017-2024.json"
REGULARIZATION_CSV = ROOT / "data" / "raw" / "regularization_2026.csv"
OUT_CSV_PERIOD = ROOT / "data" / "processed" / "cohort_tenure_period_test.csv"
OUT_CSV_COHORT = ROOT / "data" / "processed" / "cohort_tenure_rates.csv"
OUT_CSV_REG_SENSITIVITY = ROOT / "data" / "processed" / "cohort_tenure_regularization_sensitivity.csv"
OUT_CSV_SHARE = ROOT / "data" / "processed" / "cohort_share_test.csv"
OUT_CSV_VS_SPANISH = ROOT / "data" / "processed" / "cohort_vs_spanish_test.csv"
OUT_CHART = ROOT / "data" / "processed" / "cohort_tenure_rate_ratio.png"
OUT_CHART_REG_SENSITIVITY = ROOT / "data" / "processed" / "cohort_tenure_regularization_sensitivity.png"
OUT_CHART_SHARE_ALL = ROOT / "data" / "processed" / "cohort_share_test_all_groups.png"
OUT_CSV_FIXED_CUTOFF = ROOT / "data" / "processed" / "cohort_tenure_fixed_cutoff_test.csv"
OUT_CSV_FIXED_CUTOFF_REG = ROOT / "data" / "processed" / "cohort_tenure_fixed_cutoff_regularization_sensitivity.csv"
OUT_CHART_FIXED_CUTOFF = ROOT / "data" / "processed" / "cohort_tenure_fixed_cutoff_test.png"

MIR_NAME = {"MA": "MARRUECOS", "DZ": "ARGELIA"}
# Extension groups (Test C only -- see module docstring "EXTENSION").
SOUTH_AMERICA_NAMES = {"COLOMBIA", "ECUADOR", "PERU", "VENEZUELA", "VENUZUELA",
                        "BOLIVIA", "PARAGUAY", "ARGENTINA"}
EU_EUROPE_NAMES = {"RUMANIA", "ALEMANIA", "ITALIA", "FRANCIA", "BULGARIA",
                    "PORTUGAL", "POLONIA", "BELGICA", "HOLANDA"}
COHORT_WINDOW_YEARS = 3          # trailing window (V25, net-stock-delta per B42)
BASELINE_PRE2022 = [2019, 2021]  # pooled pre-2022-surge MIR report years
BASELINE_PRE2019 = [2019]        # earliest available single MIR report year
BASELINE_PRE2020_DEEP = [2017, 2018, 2019]  # NEW (B42): deeper pre-surge
    # baseline, real per-country data since T83/T87, further removed from the
    # divergence report's own ~2018-2019 surge-onset estimate for Algeria
    # than the pre-2022 baseline's 2021 component. Algeria has no 2017 row
    # (wasn't in that year's MIR top-N) -- available_years() restricts
    # pooling to years actually present per group, so this baseline is
    # effectively 2018+2019 for Algeria vs 2017+2018+2019 for Morocco;
    # baseline_years_used records exactly which years were pooled per row.
TEST_YEARS = [2022, 2023, 2024]
AGE_BANDS_15_59 = {"15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59"}
REGULARIZATION_REFERENCE_YEAR = 2024  # sex-split reference, matches T85


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

    The 'flow' series (gross immigration inflow) is still loaded here for
    completeness/other potential uses, but Test B no longer consumes it as
    of B42 -- see cohort_pop_for_year()."""
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
    docstring Test E. 2017/2018 reports (added T83/T87) carry the same
    foreign_pct/perp_male_pct/region-total fields as 2019+, so this works
    unchanged for the deeper baseline."""
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


def estimate_spanish_male_15_59(years):
    """Spanish-only male 15-59 population per year, read directly from INE
    t.56936 (T94/B44/V46). Previously this approximated Spanish population
    as `male_15_59_total - foreign_stock * working_age_share` -- a cruder,
    doubly-derived estimate (used the OVERALL population's working-age
    share as a proxy for the foreign population's own working-age share,
    then subtracted from a total sourced on a different reference date
    than the foreign figure). Covers 2002+ only (V46, no pre-2002
    backfill) -- callers requesting earlier years get no entry for them."""
    spanish_male_15_59 = {}
    with open(POPULATION_NATIONALITY_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["nationality"] == "spanish" and r["sex"] == "male" and r["age_group"] in AGE_BANDS_15_59:
                y = int(r["year"])
                spanish_male_15_59[y] = spanish_male_15_59.get(y, 0) + float(r["population_july1"])
    return {y: spanish_male_15_59[y] for y in years if y in spanish_male_15_59}


def load_regularization_added_male_15_59(codes, reference_year=REGULARIZATION_REFERENCE_YEAR):
    """{country_code: added_male_15_59} -- T85-style upper-bound regularization
    sensitivity (see module docstring EXTENSION): the entire 2026
    regularization-application pool for that nationality, assumed (a)
    already resident throughout the whole 2019-2024 window, (b) 100% aged
    15-59, (c) split male/female per that nationality's own real
    reference-year registered 15-59 sex ratio (not a flat 50/50). Mirrors
    compute_regularization_sensitivity.py (T85) exactly, applied here to
    Test B's stock series instead of the flat peligrosity denominator."""
    reg = {}
    with open(REGULARIZATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["iso2"] in codes:
                reg[r["iso2"]] = float(r["applications_estimated"])

    sex_stock = {c: {"male": 0, "female": 0} for c in codes}
    with open(MIGRATION_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["series"] == "stock_nationality" and r["country_of_origin"] in codes
                    and r["sex"] in ("male", "female") and r["age_group"] in AGE_BANDS_15_59
                    and int(r["year"]) == reference_year):
                sex_stock[r["country_of_origin"]][r["sex"]] += int(r["value"])

    result = {}
    for code in codes:
        male, female = sex_stock[code]["male"], sex_stock[code]["female"]
        male_share = male / (male + female)
        result[code] = reg.get(code, 0.0) * male_share
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


def available_years(years, crime_by_year):
    """Restrict a candidate baseline/test year list to years actually present
    in a group's crime dict -- needed because Algeria has no 2017 entry
    (wasn't in that year's MIR top-N), so BASELINE_PRE2020_DEEP is 2 years
    for Algeria vs 3 for Morocco. Keeps numerator (crime) and denominator
    (stock) pooling consistent -- both sum over the same actual year set,
    rather than crime silently summing fewer years than stock would."""
    return [y for y in years if y in crime_by_year]


def cohort_pop_for_year(stock_by_year, year, window=COHORT_WINDOW_YEARS):
    """Net-stock-delta cohort proxy (B42, replaces the old gross-trailing-
    inflow proxy): cohort_pop(year) = stock(year) - stock(year - window),
    i.e. the net change in registered stock over the window. Both this and
    settled_pop (= stock(year - window), computed by the caller) derive from
    the SAME stock_nationality series, so settled_pop is bounded and
    well-behaved by construction -- a real historical stock value, not a
    residual of two independently-measured series (gross flow vs net stock)
    that can blow up. Caveat: any churn within the pre-existing settled
    sub-population during the window (naturalization, death, re-emigration)
    is silently absorbed into this net delta, which can understate true
    recent-arrival volume -- a standard, much smaller-order demographic
    approximation than the flaw it replaces, and needs no new data (V25)."""
    return stock_by_year[year] - stock_by_year[year - window]


# ── Test A: period-level, whole nationality group, vs three baselines ──────

def run_test_a(group_name, code, stock_by_year, crime_by_year):
    rows = []
    baselines = {
        "pre_2022_pooled_2019_2021": BASELINE_PRE2022,
        "pre_2019_only": BASELINE_PRE2019,
        "pre_2020_pooled_2017_2019": BASELINE_PRE2020_DEEP,  # NEW, B42
    }
    test_windows = {str(y): [y] for y in TEST_YEARS}
    test_windows["pooled_2022_2024"] = TEST_YEARS

    for baseline_label, baseline_years_raw in baselines.items():
        baseline_years = available_years(baseline_years_raw, crime_by_year)
        if not baseline_years:
            continue
        c_base = sum(crime_by_year[y][0] for y in baseline_years)
        e_base = sum(stock_by_year[y] for y in baseline_years)
        for test_label, test_yrs_raw in test_windows.items():
            test_yrs = available_years(test_yrs_raw, crime_by_year)
            if not test_yrs:
                continue
            c_test = sum(crime_by_year[y][0] for y in test_yrs)
            e_test = sum(stock_by_year[y] for y in test_yrs)
            result = poisson_rate_ratio_test(c_base, e_base, c_test, e_test)
            if result is None:
                continue
            rows.append({
                "group": group_name, "country_code": code,
                "baseline": baseline_label, "baseline_years_used": ",".join(map(str, baseline_years)),
                "test_period": test_label,
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

def spanish_rate_for_years(years, spanish_data, spanish_male_pop):
    """Pooled Spanish-male-15-59 sexual-crime rate over a set of years --
    reuses Test E's already-loaded data to build a societal-trend adjustment
    for Test B (B43)."""
    c = sum(spanish_data[y]["spanish_male_count"] for y in years)
    n = sum(spanish_male_pop[y] for y in years)
    return c / n


def trend_adjusted_cohort_stat(c_year, s_year, p_year, r_base, trend, var_r_base):
    """Shared statistic for Test B (rolling window) and Test F (fixed
    cutoff): given one year's settled/cohort split (s_year/p_year), the
    pre-surge settled rate r_base + its Poisson variance var_r_base, and a
    reference-population trend adjustment, compute the trend-adjusted
    settled expectation, the implied cohort rate, the rate ratio, and a
    z/p-value via the delta method (B43). Returns a dict; hypothesis_call
    is left to the caller (both tests use the same negative-residual
    "undefined" guard, but the exact label differs slightly)."""
    r_expected_settled = r_base * trend
    residual = c_year - r_expected_settled * s_year
    r_cohort = residual / p_year
    rate_ratio = r_cohort / r_expected_settled

    d_dC = 1 / (r_expected_settled * p_year)
    d_drbase = -c_year * trend / (p_year * r_expected_settled ** 2)
    var_ratio = (d_dC ** 2) * poisson_var(c_year) + (d_drbase ** 2) * var_r_base
    se = math.sqrt(var_ratio)
    z = (rate_ratio - 1) / se
    p_value = math.erfc(abs(z) / math.sqrt(2))
    return {
        "r_expected_settled": r_expected_settled, "r_cohort_implied": r_cohort,
        "rate_ratio": rate_ratio, "z": z, "p_value": p_value,
    }


UNDEFINED_NEGATIVE_RESIDUAL = ("undefined (implied cohort rate negative -- trend-adjusted "
                               "settled expectation exceeds observed total; not a valid rate, see B43 caveat)")


def run_test_b(group_name, code, stock_by_year, crime_by_year, baseline_years_raw, baseline_label,
               spanish_data, spanish_male_pop, extra_stock=0):
    """extra_stock (B43, revised from B42): a constant hypothetical hidden
    population (regularization-sensitivity extension), assumed -- per the
    2026 regularización's own eligibility bar and the fact that its purpose
    was to catch people ordinary multi-year residency-based channels
    (arraigo) miss -- to be RECENT arrivals, not long-settled: it is added to
    cohort_pop every year (constant, matching T85's own "no arrival-timing
    data, so hold constant across years" convention), not to settled_pop.
    settled_pop stays the raw registered stock from `window` years ago,
    untouched by this adjustment.

    r_expected_settled (B43, replaces a frozen r_settled_baseline): the
    original version assumed the settled sub-population's rate stays frozen
    at the historical pre-surge level in every test year -- but Test E
    independently shows the REFERENCE Spanish population's own rate rose
    11%-34% over the same span (a broad, non-migration-specific rise, e.g.
    from the LO10/2022 reform). Freezing settled at the old baseline while
    the whole of Spanish society moved on forces 100% of that broad societal
    rise onto the tiny cohort bucket alongside any real cohort-specific
    effect, inflating the apparent cohort/settled rate ratio. Fixed by
    scaling the settled baseline rate by the same societal trend observed in
    the Spanish reference population between baseline and test year:
    r_expected_settled(year) = r_settled_baseline * spanish_trend(year),
    spanish_trend(year) = spanish_rate(year) / spanish_rate(baseline_years).
    The residual attributed to cohort is now the excess ABOVE what a
    society-wide (not cohort-specific) rise would already predict for the
    settled sub-population, not the excess above a rate frozen a decade
    earlier."""
    baseline_years = available_years(baseline_years_raw, crime_by_year)
    years_needed = sorted(set(baseline_years) | set(TEST_YEARS))
    settled_by_year = {y: stock_by_year[y - COHORT_WINDOW_YEARS] for y in years_needed}
    cohort_by_year = {y: cohort_pop_for_year(stock_by_year, y) + extra_stock for y in years_needed}

    c_base = sum(crime_by_year[y][0] for y in baseline_years)
    n_base_total = sum(stock_by_year[y] + extra_stock for y in baseline_years)
    r_base = c_base / n_base_total
    var_r_base = poisson_var(c_base) / n_base_total ** 2
    spanish_rate_base = spanish_rate_for_years(baseline_years, spanish_data, spanish_male_pop)

    rows = []
    for y in baseline_years:
        rows.append({
            "group": group_name, "country_code": code, "baseline": baseline_label, "year": y,
            "role": "baseline",
            "crime_male": crime_by_year[y][0], "crime_confidence": crime_by_year[y][1],
            "settled_pop_male_15_59": settled_by_year[y],
            "cohort_pop_male_15_59": cohort_by_year[y],
            "cohort_window": f"{y - COHORT_WINDOW_YEARS}->{y} (net delta)",
            "regularization_added_male_15_59": extra_stock,
            "r_settled_baseline": r_base, "spanish_trend_adjustment": 1.0, "r_expected_settled": r_base,
            "r_cohort_implied": "", "rate_ratio": "", "z": "", "p_value": "",
            "hypothesis_call": "n/a (baseline year)",
        })

    for y in TEST_YEARS:
        c_year, conf = crime_by_year[y]
        s_year, p_year = settled_by_year[y], cohort_by_year[y]
        trend = (spanish_rate_for_years([y], spanish_data, spanish_male_pop) / spanish_rate_base)
        stat = trend_adjusted_cohort_stat(c_year, s_year, p_year, r_base, trend, var_r_base)
        hyp_call = (UNDEFINED_NEGATIVE_RESIDUAL if stat["r_cohort_implied"] < 0
                    else classify(stat["rate_ratio"], stat["p_value"]))

        rows.append({
            "group": group_name, "country_code": code, "baseline": baseline_label, "year": y,
            "role": "test",
            "crime_male": c_year, "crime_confidence": conf,
            "settled_pop_male_15_59": s_year,
            "cohort_pop_male_15_59": p_year,
            "cohort_window": f"{y - COHORT_WINDOW_YEARS}->{y} (net delta)",
            "regularization_added_male_15_59": extra_stock,
            "r_settled_baseline": r_base, "spanish_trend_adjustment": trend,
            **stat,
            "hypothesis_call": hyp_call,
        })
    return rows


# ── Test F: fixed-cutoff cohort/settled split (vs Test B's rolling window) ─

FIXED_COHORT_CUTOFFS = [2022, 2024]  # user-requested (2026-07-30): treat "new
    # cohort" as everyone who arrived at/after this year, everyone before it
    # as the settled baseline population -- a single, literal before/after
    # split matching the original "modern stock vs pre-2020/2022 population"
    # framing directly, as opposed to Test B's rolling 3-year trailing
    # window (which redefines "recent" relative to every observation year).

BAD_CRIME_YEARS = {2020}  # B38: victim-side data corrupted that year;
    # perpetrator-side is fine but excluded for consistency, matching the
    # rest of this module's convention.


def run_test_f(group_name, code, stock_by_year, crime_by_year, cutoff_year,
                spanish_data, spanish_male_pop, extra_stock=0):
    """Fixed-cutoff cohort/settled split: settled_pop is pinned ONCE at
    stock(cutoff_year - 1) and held fixed for every test year >=
    cutoff_year (unlike Test B, where settled_pop is recomputed every year
    via a rolling trailing window); cohort_pop = stock(year) - settled_pop
    (+ extra_stock, assumed to have arrived at/after the cutoff -- same
    reasoning as B43's regularization reassignment, just anchored to an
    explicit cutoff instead of a rolling window). The baseline rate is
    estimated from EVERY available real MIR year strictly before the
    cutoff (not just a pooled 2-3-year set) -- the deepest, most literal
    "before" period this data supports for that specific cutoff. Settled's
    expected rate is trend-adjusted against the Spanish reference
    population exactly as in Test B (same reasoning, same helper,
    trend_adjusted_cohort_stat())."""
    baseline_years_candidates = [y for y in range(2017, cutoff_year) if y not in BAD_CRIME_YEARS]
    baseline_years = available_years(baseline_years_candidates, crime_by_year)
    test_years = [y for y in TEST_YEARS if y >= cutoff_year]

    c_base = sum(crime_by_year[y][0] for y in baseline_years)
    n_base_total = sum(stock_by_year[y] for y in baseline_years)
    r_base = c_base / n_base_total
    var_r_base = poisson_var(c_base) / n_base_total ** 2
    spanish_rate_base = spanish_rate_for_years(baseline_years, spanish_data, spanish_male_pop)

    settled_pop = stock_by_year[cutoff_year - 1]

    rows = []
    for y in test_years:
        c_year, conf = crime_by_year[y]
        cohort_pop = stock_by_year[y] - settled_pop + extra_stock
        trend = (spanish_rate_for_years([y], spanish_data, spanish_male_pop) / spanish_rate_base)
        stat = trend_adjusted_cohort_stat(c_year, settled_pop, cohort_pop, r_base, trend, var_r_base)
        hyp_call = (UNDEFINED_NEGATIVE_RESIDUAL if stat["r_cohort_implied"] < 0
                    else classify(stat["rate_ratio"], stat["p_value"]))

        rows.append({
            "group": group_name, "country_code": code, "cutoff_year": cutoff_year, "year": y,
            "baseline_years_used": ",".join(map(str, baseline_years)),
            "crime_male": c_year, "crime_confidence": conf,
            "settled_pop_male_15_59_fixed": settled_pop,
            "cohort_pop_male_15_59": cohort_pop,
            "regularization_added_male_15_59": extra_stock,
            "r_settled_baseline": r_base, "spanish_trend_adjustment": trend,
            **stat,
            "hypothesis_call": hyp_call,
        })
    return rows


# ── Test C: share of total crimes, vs three baselines ──────────────────────

def run_test_c(group_name, code, crime_total_by_year, spanish_data):
    rows = []
    baselines = {
        "pre_2022_pooled_2019_2021": BASELINE_PRE2022,
        "pre_2019_only": BASELINE_PRE2019,
        "pre_2020_pooled_2017_2019": BASELINE_PRE2020_DEEP,  # NEW, B42
    }
    test_windows = {str(y): [y] for y in TEST_YEARS}
    test_windows["pooled_2022_2024"] = TEST_YEARS

    for baseline_label, baseline_years_raw in baselines.items():
        baseline_years = available_years(baseline_years_raw, crime_total_by_year)
        if not baseline_years:
            continue
        x_base = sum(crime_total_by_year[y] for y in baseline_years)
        n_base = sum(spanish_data[y]["total_perp"] for y in baseline_years)
        for test_label, test_yrs_raw in test_windows.items():
            test_yrs = available_years(test_yrs_raw, crime_total_by_year)
            if not test_yrs:
                continue
            x_test = sum(crime_total_by_year[y] for y in test_yrs)
            n_test = sum(spanish_data[y]["total_perp"] for y in test_yrs)
            result = two_proportion_z_test(x_base, n_base, x_test, n_test)
            if result is None:
                continue
            rows.append({
                "group": group_name, "country_code": code,
                "baseline": baseline_label, "baseline_years_used": ",".join(map(str, baseline_years)),
                "test_period": test_label,
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
        "pre_2020_pooled_2017_2019": BASELINE_PRE2020_DEEP,  # NEW, B42
    }
    test_windows = {str(y): [y] for y in TEST_YEARS}
    test_windows["pooled_2022_2024"] = TEST_YEARS

    for baseline_label, baseline_years_raw in baselines.items():
        baseline_years = available_years(baseline_years_raw, crime_by_year)
        if not baseline_years:
            continue
        c_base_g = sum(crime_by_year[y][0] for y in baseline_years)
        n_base_g = sum(stock_by_year[y] for y in baseline_years)
        c_base_es = sum(spanish_data[y]["spanish_male_count"] for y in baseline_years)
        n_base_es = sum(spanish_male_pop[y] for y in baseline_years)
        for test_label, test_yrs_raw in test_windows.items():
            test_yrs = available_years(test_yrs_raw, crime_by_year)
            if not test_yrs:
                continue
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
                "baseline": baseline_label, "baseline_years_used": ",".join(map(str, baseline_years)),
                "test_period": test_label,
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
    all_years = sorted(set(BASELINE_PRE2022) | set(BASELINE_PRE2019) | set(BASELINE_PRE2020_DEEP)
                        | set(TEST_YEARS))
    spanish_male_pop = estimate_spanish_male_15_59(all_years)

    per_group = {}
    for code, name in MIR_NAME.items():
        per_group[code] = {
            "name": name,
            "stock": migration[(code, "stock")],
            "crime": crimes[name],
            "crime_total": crime_totals[name],
        }

    combined_stock, combined_crime, combined_crime_total = {}, {}, {}
    for code in MIR_NAME:
        g = per_group[code]
        for y, v in g["stock"].items():
            combined_stock[y] = combined_stock.get(y, 0) + v
        for y, (m, conf) in g["crime"].items():
            prev_m, prev_conf = combined_crime.get(y, (0, "high"))
            worse_conf = conf if conf != "high" else prev_conf
            combined_crime[y] = (prev_m + m, worse_conf)
        for y, v in g["crime_total"].items():
            combined_crime_total[y] = combined_crime_total.get(y, 0) + v
    per_group["MA+DZ"] = {"name": "MARRUECOS+ARGELIA",
                           "stock": combined_stock, "crime": combined_crime,
                           "crime_total": combined_crime_total}

    reg_added = load_regularization_added_male_15_59(list(MIR_NAME.keys()))
    reg_added["MA+DZ"] = reg_added["MA"] + reg_added["DZ"]

    rows_a, rows_b, rows_b_reg, rows_c, rows_e = [], [], [], [], []
    rows_f, rows_f_reg = [], []
    for code, g in per_group.items():
        rows_a += run_test_a(g["name"], code, g["stock"], g["crime"])
        rows_b += run_test_b(g["name"], code, g["stock"], g["crime"],
                              BASELINE_PRE2022, "pre_2022_pooled_2019_2021",
                              spanish_data, spanish_male_pop)
        rows_b += run_test_b(g["name"], code, g["stock"], g["crime"],
                              BASELINE_PRE2020_DEEP, "pre_2020_pooled_2017_2019",
                              spanish_data, spanish_male_pop)
        rows_b_reg += run_test_b(g["name"], code, g["stock"], g["crime"],
                                  BASELINE_PRE2022, "pre_2022_pooled_2019_2021",
                                  spanish_data, spanish_male_pop, extra_stock=reg_added[code])
        rows_b_reg += run_test_b(g["name"], code, g["stock"], g["crime"],
                                  BASELINE_PRE2020_DEEP, "pre_2020_pooled_2017_2019",
                                  spanish_data, spanish_male_pop, extra_stock=reg_added[code])
        rows_c += run_test_c(g["name"], code, g["crime_total"], spanish_data)
        rows_e += run_test_e(g["name"], code, g["stock"], g["crime"], spanish_male_pop, spanish_data)
        for cutoff in FIXED_COHORT_CUTOFFS:
            rows_f += run_test_f(g["name"], code, g["stock"], g["crime"], cutoff,
                                  spanish_data, spanish_male_pop)
            rows_f_reg += run_test_f(g["name"], code, g["stock"], g["crime"], cutoff,
                                      spanish_data, spanish_male_pop, extra_stock=reg_added[code])

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

    with open(OUT_CSV_REG_SENSITIVITY, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_b_reg[0].keys()))
        w.writeheader()
        w.writerows(rows_b_reg)
    print(f"Wrote {len(rows_b_reg)} rows -> {OUT_CSV_REG_SENSITIVITY}")

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

    with open(OUT_CSV_FIXED_CUTOFF, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_f[0].keys()))
        w.writeheader()
        w.writerows(rows_f)
    print(f"Wrote {len(rows_f)} rows -> {OUT_CSV_FIXED_CUTOFF}")

    with open(OUT_CSV_FIXED_CUTOFF_REG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_f_reg[0].keys()))
        w.writeheader()
        w.writerows(rows_f_reg)
    print(f"Wrote {len(rows_f_reg)} rows -> {OUT_CSV_FIXED_CUTOFF_REG}")

    print("\nTEST A -- period-level (whole nationality group, recent stock vs original stock):")
    for r in rows_a:
        print(f"  {r['group']:20} {r['baseline']:26} vs {r['test_period']:16} "
              f"rate_ratio={r['rate_ratio']:.2f}  z={r['z']:+.2f}  p={r['p_value']:.4f}  {r['hypothesis_call']}")

    print("\nTEST B -- cohort-specific (recent-arrival cohort vs settled sub-population, net-delta + trend-adj., B42/B43):")
    for r in rows_b:
        if r["role"] == "test":
            print(f"  {r['group']:20} [{r['baseline']}] {r['year']}  rate_ratio={r['rate_ratio']:.2f}  "
                  f"z={r['z']:+.2f}  p={r['p_value']:.4f}  {r['hypothesis_call']}")

    print("\nTEST B (regularization-adjusted sensitivity, upper bound per T85 assumptions):")
    for r in rows_b_reg:
        if r["role"] == "test":
            print(f"  {r['group']:20} [{r['baseline']}] {r['year']}  +{r['regularization_added_male_15_59']:.0f} "
                  f"cohort  rate_ratio={r['rate_ratio']:.2f}  z={r['z']:+.2f}  p={r['p_value']:.4f}  "
                  f"{r['hypothesis_call']}")

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

    print("\nTEST F -- fixed-cutoff cohort/settled split (unadjusted):")
    for r in rows_f:
        print(f"  {r['group']:20} cutoff={r['cutoff_year']} {r['year']}  rate_ratio={r['rate_ratio']:.2f}  "
              f"z={r['z']:+.2f}  p={r['p_value']:.4f}  {r['hypothesis_call']}")

    print("\nTEST F (regularization-adjusted, assumed to have arrived at/after the cutoff):")
    for r in rows_f_reg:
        print(f"  {r['group']:20} cutoff={r['cutoff_year']} {r['year']}  "
              f"+{r['regularization_added_male_15_59']:.0f} cohort  rate_ratio={r['rate_ratio']:.2f}  "
              f"z={r['z']:+.2f}  p={r['p_value']:.4f}  {r['hypothesis_call']}")

    make_chart(rows_a, rows_b, rows_c, rows_e)
    make_reg_sensitivity_chart(rows_b, rows_b_reg)
    make_fixed_cutoff_chart(rows_f, rows_f_reg)
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

    # Row 2: Test B -- cohort vs settled residual, both baselines overlaid (B42)
    for ax, g in zip(axes[1], groups):
        for baseline_label, marker, offset in [
            ("pre_2022_pooled_2019_2021", "o", -0.06),
            ("pre_2020_pooled_2017_2019", "^", 0.06),
        ]:
            rs = [r for r in rows_b if r["group"] == g and r["role"] == "test"
                  and r["baseline"] == baseline_label]
            if not rs:
                continue
            years = [r["year"] + offset for r in rs]
            ratios = [r["rate_ratio"] for r in rs]
            colors = ["tab:red" if r["p_value"] < 0.05 else "tab:blue" for r in rs]
            ax.scatter(years, ratios, c=colors, s=60, zorder=3, marker=marker,
                       label=baseline_label.replace("pooled_", ""))
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_title(f"Test B: {g}\n(cohort/settled, net-delta + trend-adj., B42/B43)")
        ax.set_xlabel("year")
        ax.set_xticks(TEST_YEARS)
    axes[1][0].set_ylabel("rate ratio (implied cohort / settled baseline)\no=pre-2022 baseline, ^=deep pre-2020 baseline\nred=p<0.05")
    axes[1][0].legend(fontsize=6, loc="upper left")

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


def make_reg_sensitivity_chart(rows_b, rows_b_reg):
    """Test B, unadjusted vs regularization-adjusted (B42/T85 extension) --
    how much does assuming the full regularization-application pool was
    already-settled shift the implied cohort/settled rate ratio."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = ["MARRUECOS", "ARGELIA", "MARRUECOS+ARGELIA"]
    baseline_label = "pre_2020_pooled_2017_2019"

    fig, axes = plt.subplots(1, len(groups), figsize=(4 * len(groups), 4.5), sharey=True)
    for ax, g in zip(axes, groups):
        orig = [r for r in rows_b if r["group"] == g and r["role"] == "test"
                and r["baseline"] == baseline_label]
        adj = [r for r in rows_b_reg if r["group"] == g and r["role"] == "test"
               and r["baseline"] == baseline_label]
        years = [r["year"] for r in orig]
        x = range(len(years))
        w = 0.35
        ax.bar([i - w / 2 for i in x], [r["rate_ratio"] for r in orig], w,
               label="Unadjusted", color="#4C72B0")
        ax.bar([i + w / 2 for i in x], [r["rate_ratio"] for r in adj], w,
               label="+ regularization pool (upper bound)", color="#DD8452")
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_xticks(list(x))
        ax.set_xticklabels(years, fontsize=8)
        ax.set_title(g.title(), fontsize=10)
        ax.set_ylabel("implied cohort/settled rate ratio", fontsize=8)
    axes[0].legend(fontsize=7, loc="upper left")
    fig.suptitle("Test B sensitivity: adding the 2026 regularization pool to cohort_pop (B43/T85)\n"
                 f"baseline={baseline_label}; upper bound, not a best estimate (V14) -- association only")
    fig.tight_layout()
    fig.savefig(OUT_CHART_REG_SENSITIVITY, dpi=150)
    print(f"Wrote chart -> {OUT_CHART_REG_SENSITIVITY}")


TINY_COHORT_POP_THRESHOLD = 500  # below this, a single year's net-stock-delta
    # is so small the rate ratio is dominated by noise, not signal (e.g.
    # Argelia cutoff=2022/test=2022: cohort_pop=66, rate_ratio=52x on a
    # single extra year of accumulation since the cutoff -- flagged, not
    # hidden, since it's still a real (if unstable) computation from real
    # data (C9), but must not be allowed to swamp the chart's scale.


def make_fixed_cutoff_chart(rows_f, rows_f_reg):
    """Test F: fixed-cutoff cohort/settled split, unadjusted vs
    regularization-adjusted, one panel per group, bars grouped by
    (cutoff_year, test_year) -- cutoff=2022 has 3 test years (2022-2024),
    cutoff=2024 has only 1 (2024 itself). Log y-scale: the very first test
    year after a cutoff can have a tiny cohort_pop (barely any time has
    accumulated since the split), making its rate ratio wildly noisy and,
    on a linear scale, visually swamp every other (far more stable) bar --
    see TINY_COHORT_POP_THRESHOLD. Each bar is annotated with its own
    cohort_pop so the instability is visible directly on the chart, not
    just in the caveat text."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = ["MARRUECOS", "ARGELIA", "MARRUECOS+ARGELIA"]

    fig, axes = plt.subplots(1, len(groups), figsize=(5 * len(groups), 4.5), sharey=True)
    for ax, g in zip(axes, groups):
        orig = [r for r in rows_f if r["group"] == g]
        adj = {(r["cutoff_year"], r["year"]): r for r in rows_f_reg if r["group"] == g}
        labels = [f"cutoff={r['cutoff_year']}\ntest={r['year']}" for r in orig]
        x = list(range(len(orig)))
        w = 0.35
        bars_orig = ax.bar([i - w / 2 for i in x], [max(r["rate_ratio"], 1e-3) for r in orig], w,
                            label="Unadjusted", color="#4C72B0")
        adj_rows = [adj[(r["cutoff_year"], r["year"])] for r in orig]
        bars_adj = ax.bar([i + w / 2 for i in x], [max(r["rate_ratio"], 1e-3) for r in adj_rows], w,
                           label="+ regularization pool (upper bound)", color="#DD8452")
        for bar, r in zip(bars_orig, orig):
            note = f"n={r['cohort_pop_male_15_59']}"
            if r["hypothesis_call"].startswith("undefined"):
                note += " (undefined)"
            elif r["cohort_pop_male_15_59"] < TINY_COHORT_POP_THRESHOLD:
                note += " (tiny -- unstable)"
            ax.annotate(note, (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        fontsize=6, ha="center", va="bottom", rotation=90,
                        xytext=(0, 2), textcoords="offset points")
        ax.set_yscale("log")
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=7)
        ax.set_title(g.title(), fontsize=10)
        ax.set_ylabel("implied cohort/settled rate ratio (log scale)", fontsize=8)
    axes[0].legend(fontsize=7, loc="upper left")
    fig.suptitle("Test F -- fixed-cutoff cohort/settled split (\"arrived at/after cutoff\" vs \"everyone before\")\n"
                 "settled_pop pinned at stock(cutoff-1), Spanish-population trend-adjusted; log scale -- annotations show "
                 "cohort_pop (n); association only, upper-bound (V14)")
    fig.tight_layout()
    fig.savefig(OUT_CHART_FIXED_CUTOFF, dpi=150)
    print(f"Wrote chart -> {OUT_CHART_FIXED_CUTOFF}")


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
