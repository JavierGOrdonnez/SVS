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

**RESULT after B42 alone (superseded below, kept for the record)**: the
recent-arrival cohort's implied rate came out **significantly ABOVE** the
settled-population baseline for both countries in most years, by a factor of
1.7x-6.5x. This reversed the original (pre-B42) finding, but the magnitude —
up to 6x — was flagged by the user as implausibly large, prompting a second
look.

**CORRECTION (B43, 2026-07-30)**, applied the same day: two further issues,
both raised by the user.

1. **The regularization-sensitivity extension had assigned the hidden
   population to the wrong bucket.** B42's sensitivity variant (below) added
   the 2026 regularization-application pool to `settled_pop`, reasoning it
   was "already resident" per the regularization's eligibility bar. Too
   weak: that bar (resident before 2026-01-01) is satisfied by someone who
   arrived weeks earlier just as much as someone who arrived a decade
   earlier, and Spain's ordinary multi-year residency channels (*arraigo
   social/laboral*, 2-3 years) already exist for genuinely long-settled
   undocumented people — an *extraordinary*, lower-bar amnesty more
   plausibly catches people those ordinary channels miss, i.e. skews toward
   recent arrivals. Reassigned to `cohort_pop` instead.
2. **The settled sub-population's rate was still frozen at the historical
   baseline in every test year** — the residual (non-tautological) fix from
   B42 assumed nothing changed for settled people at all. But Test E
   (below) independently shows the *Spanish reference population's own
   rate* rose 11%-34% over the same span — a broad, non-migration-specific
   rise (e.g. from the LO10/2022 reform). Freezing settled at the old level
   while all of Spanish society moved on forced the *entire* societal-wide
   rise onto the tiny cohort bucket, on top of any real cohort-specific
   effect — this is what made the ratio implausibly large. Fixed: the
   settled baseline rate is now scaled by the same trend observed in the
   Spanish reference population between baseline and test year
   (`r_expected_settled = r_settled_baseline × spanish_trend`, reusing
   Test E's already-loaded data).

This second adjustment occasionally makes the trend-adjusted settled
expectation alone *exceed* the observed total (a negative implied cohort
rate — not a bug, but a real model-tension signal for Marruecos specifically,
whose own overall rate rose *less* than Spain's per Test E, so applying the
*full* Spanish trend to its settled sub-population overshoots). Such rows
are reported `hypothesis_call="undefined..."` rather than a spuriously
precise "significantly below baseline".

**RESULT (final, both baselines, unadjusted for regularization)**:

| Group | Baseline | 2022 | 2023 | 2024 |
|---|---|---|---|---|
| Marruecos | pre-2022 (2019+2021) | 0.79x, p=.52 (ns) | undefined (negative residual) | 0.24x, p=.004 (significantly *below*) |
| Marruecos | deep pre-2020 (2017-2019) | 1.19x, p=.59 (ns) | 0.27x, p=.038 (significantly *below*) | 0.58x, p=.13 (ns) |
| Argelia | pre-2022 (2019+2021) | 1.88x, p=.42 (ns) | 2.19x, p=.24 (ns) | 3.55x, p=.0008 (H2) |
| Argelia | deep pre-2020 (2017-2019) | 1.63x, p=.57 (ns) | 1.94x, p=.36 (ns) | 3.35x, p=.002 (H2) |

**Marruecos now shows NO significant cohort elevation in any comparison** —
consistent with, not contradicting, Test E's own finding that Marruecos's
overall rate rose *less* than Spain's. **Argelia shows a real, moderate,
consistently significant cohort elevation specifically by 2024** (ratio
3.3x-3.6x depending on baseline; non-significant 2022-2023) — consistent
with Test E's finding that Argelia's overall rate rose *more* than Spain's.
This ties together far more coherently with Tests A/E than either the
original (pre-B42) or the B42-only (frozen-baseline) result did.

**Regularization-adjusted sensitivity (mirrors T84, corrected B43)**: since
MIR/Eurostat stock only counts *registered* residents, and Test B's
decomposition is therefore blind to any undocumented population, a
sensitivity variant adds the 2026 regularization-application pool for that
nationality — assumed (a) already present throughout the whole window, (b)
100% aged 15-59, (c) split male/female per that nationality's own real sex
ratio, exactly as T84 does for the flat peligrosity rate — to `cohort_pop`
(not `settled_pop`, see correction above) every year, constant, matching
T84's own "no arrival-timing data" convention. **This moves the ratio
toward 1** for both countries (mechanically: the same residual crime count
is now divided by a larger cohort population): Marruecos 0.65x-0.96x
(pre-2022 baseline, all ns) / 0.90x-1.22x (deep baseline, all ns — the
previously-undefined 2023 row now resolves to a valid 0.90x); Argelia
1.25x-2.28x (pre-2022 baseline) / 1.29x-2.33x (deep baseline) — Argelia's
2024 signal survives this adjustment
(remains significant, p<.0001 both baselines), Marruecos's absence of a
signal is unchanged. Explicit upper bound (V14), association only — we have
no true arrival-year data for regularization applicants, so this is the
more defensible of the two buckets to place them in, not a claim about
actual tenure.

**Synthesis (A vs B), corrected twice (B42, then B43)**: Test A shows the
*whole* nationality group's rate rose significantly after 2022 for both
countries. Test B, once its three design flaws (gross-inflow cohort proxy,
tautological settled baseline, frozen settled-rate ignoring the documented
Spanish-population trend) are fixed, shows this is **not** uniform across
countries: for Marruecos there's no evidence the rise is cohort-specific
(consistent with Marruecos's own rise trailing Spain's, per Test E); for
Argelia there is a real, moderate, cohort-specific signal by 2024
(consistent with Argelia's rise outpacing Spain's). This should still be
read with appropriate caution: Test B's cohort/settled split remains an
approximation (net-stock-delta absorbs any churn in the pre-existing
settled sub-population — naturalization, death, re-emigration — into the
cohort residual, which can understate true recent-arrival volume), the
trend adjustment assumes the settled sub-population's rate moves exactly in
lockstep with the *whole* Spanish reference population's (no independent
settled-specific trend exists to check this against), and the baseline
periods themselves are short (2-3 real MIR report years).

Denominators = settled_pop/cohort_pop, now a net-stock-delta on the real,
non-extrapolated Eurostat joint cross for MA/DZ (V25, corrected B42/B43).

## Test F — fixed-cutoff cohort/settled split (added 2026-07-30, user request)

Test B's rolling 3-year window redefines "recent arrival" relative to
*every* observation year — it doesn't literally match this investigation's
original framing ("modern stock vs. the pre-2020/2022 population"). Test F
uses a single, fixed calendar cutoff instead: `settled_pop` is pinned ONCE
at `stock(cutoff_year − 1)` and held fixed for every test year at/after the
cutoff (not recomputed per year); `cohort_pop = stock(year) − settled_pop`.
Run for two cutoffs, each with the deepest available pre-cutoff baseline
(every real MIR year strictly before that cutoff, 2020 excluded per B38) and
the same Spanish-population trend adjustment as Test B:

- **cutoff=2022** ("arrived 2022 onward" vs. "everyone here before 2022"):
  test years 2022, 2023, 2024 — `cohort_pop` grows each year as more time
  accumulates since the cutoff. Baseline: 2017-2019+2021 (Marruecos),
  2018-2019+2021 (Argelia, no 2017 row).
- **cutoff=2024** ("arrived 2024 onward" vs. "everyone here before 2024"):
  test year 2024 only — the narrowest, most literal "just the newest
  arrivals" comparison, with the deepest possible baseline (everything
  through 2023 counts as "before"). Baseline: 2017-2019+2021-2023
  (Marruecos), 2018-2019+2021-2023 (Argelia).

**RESULT (unadjusted)**:

| Group | cutoff=2022, test=2022 | test=2023 | test=2024 | cutoff=2024, test=2024 |
|---|---|---|---|---|
| Marruecos | 2.46x, p=.58 (ns) | undefined (negative residual) | 0.57x, p=.10 (ns) | 0.05x, p=.08 (ns) |
| Argelia | **52.16x, p=.36 (ns, see caveat)** | 2.67x, p=.19 (ns) | 3.61x, p=.0002 (H2) | 4.59x, p=.0003 (H2) |

**Marruecos shows no significant elevation under any cutoff** — a third
independent confirmation (alongside Test B and Test E) that Marruecos's rise
isn't concentrated in recent arrivals specifically. **Argelia shows a real,
significant elevation at both of the two "deep-accumulation" cells**
(cutoff=2022/test=2024: 3.61x; cutoff=2024/test=2024: 4.59x) — this is a
meaningful convergence: Test B (rolling window) and Test F (fixed cutoff)
are two genuinely different ways of drawing the cohort/settled line, and
both independently land on a significant ~3-5x Argelia-specific 2024 signal,
which is good evidence this isn't an artifact of either particular windowing
choice.

**Caveat — the cutoff=2022/test=2022 cell is unstable, not a real 52x
finding.** Only one year (2022) has elapsed since the settled_pop reference
point (stock at end of 2021), so `cohort_pop` is tiny: 66 people for
Argelia, 5,532 for Marruecos. Dividing a Poisson-noisy residual by a
denominator that small produces a wildly unstable point estimate (Argelia's
52.16x, still correctly reported as non-significant, p=.36, but the point
estimate itself shouldn't be read as a real effect size) — flagged directly
on the chart (log-scale y-axis, each bar annotated with its own `cohort_pop`
and a "(tiny — unstable)" note where n<500) rather than hidden or silently
trusted (C9).

**Regularization-adjusted variant (assumed to have arrived at/after the
cutoff)**: mirrors T84/B43's reasoning, now anchored to whichever specific
cutoff is being tested. Because Test F's accumulation windows are much
shorter than Test B's rolling 3-year window, adding the same-sized
regularization pool implies an extreme share of that period's true net
growth was undocumented — e.g. for Argelia cutoff=2022/test=2022, the
regularization pool (26,551) against a raw `cohort_pop` of just 66 implies
99.75% of that single year's net growth was undocumented; even the deepest
cell (cutoff=2024/test=2024) implies 86.6% (Argelia) / 79.1% (Marruecos)
undocumented. These are far more extreme than Test B's own regularization
variant (which spreads the same pool over a 3-year window) and should be
read as an outer, not-very-plausible upper bound (V14) rather than a
considered estimate — consistent with this reading, nearly every
regularization-adjusted cell here reports "significantly BELOW baseline"
(ratios 0.01x-0.77x), a mechanical consequence of diluting a fixed residual
crime count over a hugely inflated cohort denominator, not a genuine finding
that new arrivals under-offend.

**Synthesis (A vs B vs F)**: three independently-designed tests (Test A's
direct whole-group rate ratio, Test B's rolling-window decomposition, Test
F's fixed-cutoff decomposition) now agree: Marruecos's post-2022 rate rise
shows no evidence of being concentrated in recent arrivals specifically;
Argelia's does, specifically by 2024, at a broadly consistent magnitude
(Test B: 3.3x-3.6x; Test F: 3.6x-4.6x). This convergence across genuinely
different methodological choices is the strongest evidence this project has
for a real (not methodology-dependent) recent-arrival-specific signal for
Argelia — still association only (V9), not causal, and still resting on the
same reference-population-trend and net-stock-delta approximations flagged
throughout this report.

Output: `data/processed/cohort_tenure_fixed_cutoff_test.csv` (12 rows, both
cutoffs) + `data/processed/cohort_tenure_fixed_cutoff_regularization_sensitivity.csv`
(12 rows) + `data/processed/cohort_tenure_fixed_cutoff_test.png` (log-scale,
cohort_pop-annotated), visually verified.

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
