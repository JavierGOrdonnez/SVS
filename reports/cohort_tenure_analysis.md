# T41 — Morocco/Algeria (+ South America/EU-Europe) cohort-tenure crime-rate analysis

Full methodology, results, and caveats for T41 (`src/crime/analyze_cohort_crime_rate.py`).
SPEC.md's T41 row keeps only a summary; this file is the source of record.

Association only throughout (⊥ causal, V9).

## Test A — period-level rate ratio (Poisson, two-sample z-test)

Whole nationality group's total crime-count ÷ total male-15-59-stock rate in
each post-surge year (+ pooled 2022-2024) vs three baselines — pre-2022
(pooled 2019+2021), pre-2019 (2019 alone), and (added B42) a deeper
pre-2020 (pooled 2017-2019, real per-country data since T82/T86; Algeria has
no 2017 row, so its deep baseline is effectively 2018+2019). Directly
testable, no cohort-split assumption.

**RESULT**: rate significantly elevated and growing for both countries.
- Marruecos vs pre-2022: 2022 ratio=1.08 p=.064 (ns), 2023 ratio=1.11
  p=.012, 2024 ratio=1.16 p=.0003.
- Argelia vs pre-2022: 2022 ratio=1.22 p=.079 (ns), 2023 ratio=1.44
  p=.0005, 2024 ratio=1.90 p<.0001.
- Vs the stricter pre-2019-only baseline the pattern holds but arrives
  later (significant by 2023-2024, not 2022).
- Vs the deeper pre-2020 (2017-2019) baseline the effect is larger and
  significant everywhere: Marruecos 1.40x-1.49x (p<.0001 all 3 years),
  Argelia 1.32x-2.04x (p<.05 all 3 years) — consistent with, not
  contradicting, the pre-2022 baseline's pattern, just further from the
  surge-onset period so less attenuated.

## Test B — cohort-specific decomposition

**CORRECTION (B42, 2026-07-30)**: this section originally reported the
opposite conclusion. Re-examining the test critically (at a user's request,
not prompted by new data) surfaced two compounding design flaws in the
original implementation:

1. **Cohort population was a gross, not net, inflow proxy.** `cohort_pop`
   summed `flow_immigration_from_abroad` (gross immigration events) over a
   trailing 3-year window, never netted against emigration — no such data
   exists anywhere in this repo (N3 is still an open backlog item). This
   produced an implied **settled** population that implausibly *collapsed*
   over time (Algeria: 18,017 → 6,382 male 15-59, 2019→2024, a 65% "decline"
   in a population that was actually *growing*; Morocco similarly fell
   12%), and for Algeria specifically, cohort_pop approached the *entire*
   stock (83% of 2024 stock) — numerically degenerate exactly where the
   interesting question lives.
2. **The settled baseline rate was a tautology.** `r_settled_baseline` was
   computed as TOTAL baseline crime (settled+cohort combined) divided by the
   SETTLED-ONLY baseline population. Algebraically this equals
   `total_rate / settled_share` — a deterministic rescaling of the group's
   overall rate that is *exactly* what you'd get if cohort and settled
   sub-populations had identical rates at baseline. It assumed away the very
   question Test B claims to test, and the resulting inflation was worse the
   larger (and, per flaw 1, artificially inflated) the cohort population was
   estimated to be.

Both are fixed. **Cohort population is now a net-stock-delta**:
`cohort_pop(year) = stock(year) − stock(year−3)`, `settled_pop(year) =
stock(year−3)` directly — both terms come from the same real Eurostat
`stock_nationality` series (no separate flow series with a different
definition/coverage), so settled_pop is bounded and well-behaved by
construction; it is now monotonically *growing* for both countries, matching
this report's own "aging in place" / gradual-growth narrative rather than
contradicting it. **The settled baseline rate is now anchored to the
group's own observed total pre-surge rate** (identical to Test A's
`rate_baseline` for the same years), not a settled-only reconstruction.
Test B is also now run against a second, deeper baseline
(`pre_2020_pooled_2017_2019`, real per-country MIR data available since
T82/T86) alongside the original `pre_2022_pooled_2019_2021`, both reported
side by side.

**RESULT (reversed from the original)**: the recent-arrival cohort's
implied rate is **significantly ABOVE** the settled-population baseline for
both countries in most years tested:

| Group | Baseline | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| Marruecos | pre-2022 (2019+2021) | 1.66x, p=.075 | 2.01x, p=.017 | 2.10x, p=.001 |
| Marruecos | deep pre-2020 (2017-2019) | 4.28x, p<.0001 | 5.09x, p<.0001 | 4.66x, p<.0001 |
| Argelia | pre-2022 (2019+2021) | 2.93x, p=.112 (ns) | 4.73x, p=.004 | 5.73x, p<.0001 |
| Argelia | deep pre-2020 (2017-2019) | 3.75x, p=.042 | 5.67x, p=.001 | 6.51x, p<.0001 |

This is the opposite of what was previously published here ("Marruecos
significantly BELOW settled baseline all 3 years... Argelia below in 2022
then not significant 2023-2024"). The deeper baseline (further removed from
Algeria's own ~2018-2019 surge-onset, per `reports/algeria_morocco_divergence.md`'s
H3 section) shows an even larger and more consistently significant cohort
effect than the original pre-2022 baseline, for both countries.

**Regularization-adjusted sensitivity (new, mirrors T84)**: since MIR/Eurostat
stock only counts *registered* residents, and Test B's decomposition is
therefore blind to any undocumented population, a sensitivity variant adds
the 2026 regularization-application pool for that nationality — assumed (a)
already resident throughout the whole window, (b) 100% aged 15-59, (c) split
male/female per that nationality's own real sex ratio, exactly as T84 does
for the flat peligrosity rate — into the stock series before re-deriving
cohort_pop/settled_pop/r_base. Because cohort_pop is now a net delta, a
constant hidden population cancels out of it and lands entirely in
settled_pop, consistent with "these people were already here the whole
time." **This makes the cohort effect stronger, not weaker**: Marruecos
2.00x-2.77x (pre-2022 baseline) / 5.71x-6.99x (deep baseline); Argelia
5.16x-11.19x / 7.68x-13.59x. Explicit upper bound (V14), association only —
we have no arrival-year data for regularization applicants, so this is the
single defensible bucket to place them in, not a claim about true tenure.

**Synthesis (A vs B), corrected**: Test A shows the *whole* nationality
group's rate rose significantly after 2022. Test B, once its two design
flaws are fixed, is now consistent with (not contradicting) a story where
this rise IS concentrated in the newly-arrived cohort specifically — the
opposite of what the flawed version implied. This should still be read with
appropriate caution: Test B's cohort/settled split remains an approximation
(net-stock-delta absorbs any churn in the pre-existing settled sub-population
— naturalization, death, re-emigration — into the cohort residual, which can
understate true recent-arrival volume; a much smaller-order caveat than the
flaw it replaces, but not zero), and the baseline periods themselves are
short (2-3 real MIR report years). But there is no longer a "Test B fails to
confirm this" caveat to attach to Test A's finding.

Denominators = settled_pop/cohort_pop, now a net-stock-delta on the real,
non-extrapolated Eurostat joint cross for MA/DZ (V25, corrected B42).

Output: `data/processed/cohort_tenure_period_test.csv` (Test A, 36 rows,
3 baselines) + `data/processed/cohort_tenure_rates.csv` (Test B, 32 rows,
2 baselines) + `data/processed/cohort_tenure_regularization_sensitivity.csv`
(Test B sensitivity variant, 32 rows) + `cohort_tenure_rate_ratio.png`
(Tests A/B/C/E grid, Test B row now overlays both baselines) +
`cohort_tenure_regularization_sensitivity.png` (unadjusted vs
regularization-adjusted comparison), all visually verified.

## Test C — share of total crimes (two-proportion z-test)

Added per user follow-up ("share of total crimes went up, or... group
rate went up — and whether the increase is significantly different to
that in the Spanish male population"). Nationality group's share of ALL
identified perpetrators (both sexes — MIR's spanish_pct/foreign_pct split
isn't sex-specific), baseline vs test period. Distinct from Test A: a
group's rate can rise while its share doesn't, if the reference
population's rate also rose.

**RESULT**: Marruecos share flat/non-significant throughout (7.7-7.8%→
7.3-7.8%, all p>.1); Argelia share significantly increased from 2023 on
(0.97%→1.19% p=.047 in 2023, →1.68% p<.0001 in 2024); combined MA+DZ
share only significant vs 2024 alone (8.7%→9.3% p=.043). Vs the deeper
pre-2020 (2017-2019) baseline (added B42), Marruecos's share is instead
significantly higher in 2022/2024/pooled (6.79%→7.6-7.8%, p<.002) — the
2017-2019 window itself had a lower baseline share than 2019+2021 pooled,
so this baseline shift changes Marruecos's headline from "flat" to "share
rose" (Argelia's own pattern is materially unchanged: still rising from
2023 on under this baseline too).

## Test D — Test A per 100,000 males 15-59

Presentational restatement of Test A (same statistic/p-values, unit
conversion only); columns `rate_baseline_per_100k`/`rate_test_per_100k`
added to the Test A CSV.

## Test E — difference-in-differences (log-linear Poisson interaction z-test)

Is the group's rate ratio (test/baseline) significantly different from
the Spanish male 15-59 population's rate ratio over the same periods?
Needs a Spanish-specific male perpetrator count (approximated:
reconstructed spanish_count = foreign_total/foreign_pct − foreign_total,
from the same by_country data as T42, × report-level `perp_male_pct`) and
a Spanish-specific male 15-59 population (approximated: general
population male-15-59 total minus an estimated foreign male-15-59 subset,
assuming the foreign population shares the general population's age/sex
distribution — flagged as likely understating true foreign working-age-
male concentration, which overstates the Spanish denominator and
understates the Spanish rate LEVEL, though this bias is expected to
largely cancel in the baseline-to-test RATIO since it applies similarly
at both time points; Test E is therefore lower-confidence than Tests
A-C).

**RESULT (surprising)**: the Spanish-population rate itself also rose
substantially over 2019-2024 (rate ratio 1.11-1.34 depending on
baseline/period — consistent with a broad rise in registered
sexual-crime reports across ALL nationalities post-LO10/2022, not
migrant-specific). Against this rising Spanish baseline, Marruecos's
increase is **significantly SMALLER** than the Spanish population's
increase in most comparisons (ratio-of-ratios 0.81-0.92, p<.05 in 5 of 8
baseline/period combos); Argelia's increase is **significantly LARGER**
than the Spanish population's only vs 2024 (ratio-of-ratios 1.38-1.49,
p<.01) and pooled-2022-2024 vs the pre-2022 baseline (1.27, p=.005) — all
other Argelia comparisons non-significant. Combined MA+DZ mostly tracks
Marruecos's pattern (driven by larger N).

Test E's Spanish-population approximation is the weakest link in this
task — flagged accordingly, not silently trusted.

Vs the deeper pre-2020 (2017-2019) baseline (added B42): Marruecos's rise is
no longer significantly different from the Spanish population's in any
comparison (ratio-of-ratios 0.92-1.02, all p>.05) — a softer result than the
pre-2022 baseline's "significantly smaller" finding; Argelia's pattern is
essentially unchanged (significantly larger vs 2024 and pooled, ratio 1.24-1.44,
p<.02; other comparisons ns).

Output: `data/processed/cohort_share_test.csv` (Test C, 60 rows, 3 baselines
+ South America/EU-Europe) + `data/processed/cohort_vs_spanish_test.csv`
(Test E, 36 rows, 3 baselines) + extends `cohort_tenure_rate_ratio.png` to a
4-row grid (Tests A/B/C/E), visually verified.

## Extension — South America / EU-Europe (Test C only)

Added per user follow-up ("make this comparison for south americans, and
for europeans who are not spanish (eu and non eu)").

**Scope limit found**: only Test C is computable for these groups — Tests
A/B/D/E all need a male-15-59 population/stock TIME SERIES, and
`migration_spain.csv` has none for any country besides MA/DZ (the
Eurostat migr_imm1ctz/migr_pop1ctz joint-cross extraction, T11/V25, was
only ever run for `CITIZENS=["MA","DZ"]`); every other country has at
most a single 2025 stock snapshot, unusable for a baseline-vs-test
comparison. Extending Tests A/D/E would require the user to supply the
raw Eurostat bulk TSV files and re-running `parse_eurostat_migration_cohort.py`
with an expanded `CITIZENS` list — this is now T43/T44 (data) + T45-T48
(tests) in SPEC.md.

**South America** group = sum of individually-named South American
countries in MIR's by_country (Colombia, Ecuador, Peru,
Venezuela/Venuzuela, Bolivia, Paraguay, Argentina) — NOT MIR's own
"AMERICA" region total, which conflates South America with Central
America/Caribbean (Honduras, Dominican Republic appear as AMERICA
siblings); undercounts true South America since MIR only lists each
year's top-N countries, with the remainder folded into a
non-region-specific "RESTO"/"OTROS AMERICA" bucket.

**EU-Europe (excl. Spain)** group: 2019-2023 uses MIR's own "UNION
EUROPEA" region total directly (EU-only by construction, no undercount);
2024 renamed the region "EUROPA (EXCEPTO ESPANA)" and started mixing in
non-EU countries (Reino Unido, Ucrania) as flat siblings, so 2024's
figure is instead reconstructed by summing individually-named EU members,
likely a soft undercount vs 2019-2023 (excludes "OTROS EUROPA", which may
still hold EU nationals not in that year's top-10, e.g. Poland/
Netherlands named in earlier years but not 2024).

**Non-EU Europe**: NOT computable as a time series — pre-2024 non-EU
Europeans are inside "RESTO PAISES", an undifferentiated global residual,
not Europe-specific; only 2024 names them individually (Reino Unido,
Ucrania), a single data point, not a comparison. Skipped rather than
fabricated.

**RESULT (Test C only)**: South America share rose sharply and
significantly vs both baselines from 2023 on (pre-2022 baseline
8.54%→10.38% p<.0001 in 2023, →11.90% p<.0001 in 2024, pooled 10.21%
p<.0001); EU-Europe share fell significantly by 2024 (pre-2022 baseline
6.20%→5.24% p=.0002; pre-2019-only baseline 6.59%→5.24% p<.0001, and
pooled-2022-2024 vs pre-2019-only also significant p=.043) — driven at
least partly by the 2024 region-redefinition undercount noted above, so
the EU-Europe 2024 decline should be treated as a soft/methodological
signal, not a clean one.

Output: adds 16 rows (8 baseline/period combos × 2 groups) to the
existing `cohort_share_test.csv` (40 rows total) + new
`cohort_share_test_all_groups.png` (Test C, all 5 groups side by side),
visually verified.
