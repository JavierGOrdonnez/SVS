# T41 — Morocco/Algeria (+ South America/EU-Europe) cohort-tenure crime-rate analysis

Full methodology, results, and caveats for T41 (`src/crime/analyze_cohort_crime_rate.py`).
SPEC.md's T41 row keeps only a summary; this file is the source of record.

Association only throughout (⊥ causal, V9).

## Test A — period-level rate ratio (Poisson, two-sample z-test)

Whole nationality group's total crime-count ÷ total male-15-59-stock rate in
each post-surge year (+ pooled 2022-2024) vs two baselines — pre-2022
(pooled 2019+2021) and pre-2019 (2019 alone). Directly testable, no
cohort-split assumption.

**RESULT**: rate significantly elevated and growing for both countries.
- Marruecos vs pre-2022: 2022 ratio=1.08 p=.064 (ns), 2023 ratio=1.11
  p=.012, 2024 ratio=1.16 p=.0003.
- Argelia vs pre-2022: 2022 ratio=1.22 p=.079 (ns), 2023 ratio=1.44
  p=.0005, 2024 ratio=1.90 p<.0001.
- Vs the stricter pre-2019-only baseline the pattern holds but arrives
  later (significant by 2023-2024, not 2022).

## Test B — cohort-specific decomposition

Decomposes crime(year) = r_settled_baseline·settled_pop(year) +
r_cohort(year)·cohort_pop(year), r_settled_baseline fit from settled-only
pre-2022 population (V25 cohort/settled split) — isolates whether the
*newly arrived* sub-population specifically is elevated vs the
*already-settled* sub-population, both evaluated in the same post-surge
years.

**RESULT**: Marruecos significantly BELOW settled baseline all 3 years
(2022 ratio=0.39 p<.0001, 2023 ratio=0.56 p<.0001, 2024 ratio=0.65
p<.0001); Argelia below in 2022 (ratio=0.53 p=.007) then not significant
2023-2024 (ratio 0.85→1.23, p=.30/.10).

**Synthesis (A vs B)**: the two tests are not contradictory but answer
different questions and use different baselines (Test A's baseline is the
whole pre-2022 stock; Test B's baseline is the settled-only
sub-population, which is inherently a higher per-capita rate since it
excludes recent arrivals even in baseline years) — together they indicate
the *whole* nationality group's rate rose significantly after 2022
(Test A), but under the V25 cohort-population approximation this rise is
NOT concentrated in the newly-arrived cohort specifically (Test B) —
consistent with either a broader rate shift across the whole resident
population (settled included) or with noise/approximation error in the
cohort/settled population split. **Do not read Test A's result as
evidence that new arrivals specifically drive the increase — that is
exactly what Test B fails to confirm.**

Denominators = settled_pop/cohort_pop per V25 (real, non-extrapolated
Eurostat joint cross for MA/DZ).

Output: `data/processed/cohort_tenure_period_test.csv` (Test A, 24 rows) +
`data/processed/cohort_tenure_rates.csv` (Test B, 15 rows) +
`cohort_tenure_rate_ratio.png` (both tests, p-value-annotated, visually
verified).

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
share only significant vs 2024 alone (8.7%→9.3% p=.043).

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

Output: `data/processed/cohort_share_test.csv` (Test C, 24 rows) +
`data/processed/cohort_vs_spanish_test.csv` (Test E, 24 rows) + extends
`cohort_tenure_rate_ratio.png` to a 4-row grid (Tests A/B/C/E), visually
verified.

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
