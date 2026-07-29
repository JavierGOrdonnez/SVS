# Algeria/Morocco peligrosity divergence — why is Algeria's rate higher and rising while Morocco's is stable?

Synthesizes T41's cohort-tenure tests with three follow-up hypotheses (T76-T79, T84, N20)
prompted by the observation that Algeria's sexual-crime perpetrator rate looks high and
rising over the last ~4 years while Morocco's — a "culturally similar" country — looks
comparatively stable. Association only throughout (V9); every number below cites its
exact source per C1.

## Starting point: T41's headline (already established, see `reports/cohort_tenure_analysis.md`)

Using MIR "Informe sobre Delitos contra la Libertad Sexual" perpetrator counts (2019,
2021-2024; 2020 excluded, corrupted victim-side data per bug B38 — perpetrator-side 2020
is fine but excluded here too for consistency with the rest of this report) over Eurostat
`migr_pop1ctz` male 15-59 population stock:

- **Test A** (period rate ratio): both countries' rates rose significantly after 2022, but
  Algeria's rose further — 1.90x by 2024 (p<.0001) vs Morocco's 1.16x (p=.0003), both
  vs the pooled 2019+2021 baseline.
- **Test B** (cohort decomposition): the rise is **not** clearly concentrated in the
  newly-arrived cohort specifically for either country — inconclusive on "recent arrivals
  drove it."
- **Test E** (vs. the Spanish population's own rate rise): Morocco's increase is
  significantly **smaller** than the Spanish population's own rise in most comparisons;
  Algeria's is significantly **larger**, but only vs. 2024 and the pooled 2022-2024 period
  — not every comparison.

None of T41's tests explain *why* Algeria diverges. This report tests three concrete
hypotheses for that residual gap.

**Correction found and applied while extending this analysis (B39):** `analyze_cohort_crime_rate.py`
was broken by two undocumented regressions — a stale `ROOT` path computation left over
from the "modularize src" reorg (crashed with `FileNotFoundError` before even loading
data) and a population-denominator series-name mismatch (`stock_foreign_nationality`,
which no longer exists for Morocco/Algeria post-T66's rename to `stock_nationality`) that
also silently dropped the intended age_group≥15-59 restriction, summing the *entire*
population (all ages 0-99+) instead. Both are fixed; rerunning reproduces the originally
published figures almost exactly (e.g. Algeria's 2024 rate ratio: 1.9010886... vs. 1.90 —
unchanged to 3 significant figures), confirming the fix is a clean regression repair, not
a methodology change. See SPEC.md B39 for the full diagnostic.

## H3 — is it an age-composition effect?

**Hypothesis**: Morocco's Spain-resident population may skew older (settled for decades)
while Algeria's skews younger, and since sexual-crime conviction rates are strongly
age-dependent, comparing raw population totals (rather than age-matched populations)
could make Algeria look disproportionately elevated purely from having relatively more
men in the highest-offending age bands.

**Data limitation, confirmed directly**: MIR's sexual-crime source
(`data/raw/sexual_crimes_mir_2019-2024.json`) has **no age field anywhere** in its schema
— `nationality.perpetrators.by_country` carries country/sex/total only. A true
age×nationality-crossed numerator does not exist. A search of INE's Estadística de
Condenados table catalog turned up two candidates —
[table 28857](https://www.ine.es/jaxiT3/Tabla.htm?t=28857) ("Condenados por delitos
sexuales según sexo, edad y nacionalidad") and table 28709 — but both stop at
**continent-level** nationality ("De Africa"), not country-level; Morocco and Algeria
cannot be isolated from either. So a direct age-standardized numerator for Morocco/Algeria
specifically is not achievable with any data source currently available.

**What is achievable — indirect standardization (T76/T77)**: apply a general-population
reference age-specific conviction-rate curve (built from INE table 28857's `nationality=total`
rows over Spain's exact single-year population,
`data/processed/population_spain_estimates.csv`) to each country's own age *distribution*
(which **is** available at country level — Eurostat's real age×sex×citizenship cross for
Morocco/Algeria, continuous 2002-2025 in `migration_spain.csv`'s `stock_nationality`
series) to get an **expected** count per country if it only differed from Spain's general
population in age composition, then compare to the **observed** MIR count. This is a
standardized incidence ratio (SIR): `src/crime/compute_age_standardized_rate.py` →
`data/processed/age_standardized_rate_test.csv`.

Caveats stated plainly: the reference curve is built from **convicted** offenders (INE)
while the comparison numerator is **investigated/identified** suspects (MIR) — different
funnel stages (V15's [convicted, identified] bracket), so absolute SIR values (10x-27x)
are dominated by that funnel-stage gap, not age composition, and should not be read
literally. What *is* informative is the **ratio of Algeria's SIR to Morocco's SIR**
compared against their **crude** (unadjusted) rate ratio — since the funnel-stage bias is
shared by both countries and largely cancels in a ratio-of-ratios:

| Year | SIR ratio (DZ/MA) | Crude rate ratio (DZ/MA) | Effect of age-adjustment |
|---|---|---|---|
| 2019 | 1.58 | 1.46 | widens gap |
| 2021 | 1.57 | 1.47 | widens gap |
| 2022 | 1.80 | 1.67 | widens gap |
| 2023 | 2.05 | 1.92 | widens gap |
| 2024 | 2.53 | 2.41 | widens gap |

(`data/processed/age_standardized_dz_ma_ratio.csv`.) In **every** year, adjusting for age
composition using a common reference curve **widens**, not narrows, Algeria's gap over
Morocco — the opposite of what H3 predicts. **H3 does not explain the divergence.**

**Population-side confirmation (T76) — real, country-level Eurostat data, not an
estimate.** To be unambiguous about what does and doesn't exist here: the CRIME numerator
(MIR perpetrator counts) has no age breakdown, full stop — that's the actual gap. The
POPULATION denominator absolutely does have real age×sex×country data for Morocco and
Algeria specifically (Eurostat `migr_pop1ctz`, 5-year bands, continuous 2002-2025,
`migration_spain.csv`'s `stock_nationality` series) — this is what built the pyramid
(`docs/index.html` panel `mi-age-pyramid-dz-ma`) and the trend below. 2024 male-population
snapshot by age band:

| Age band | Morocco (male) | Algeria (male) |
|---|---|---|
| 15-19 | 25,746 | 3,221 |
| 20-24 | 43,761 | 2,958 |
| 25-29 | 53,059 | 4,520 |
| 30-34 | 54,983 | 5,097 |
| 35-39 | 58,304 | 4,593 |
| 40-44 | 63,111 | 4,393 |
| 45-49 | 54,991 | 4,896 |
| 50-54 | 37,267 | 4,849 |
| 55-59 | 22,673 | 3,430 |
| **Total 15-59** | **413,895** | **37,957** |

And the working-age composition trend (% of male 15-59 population that is 15-39, the rest
40-59; panel `mi-dz-ma-age-trend`, `src/migration/build_dashboard_data.py`'s
`_working_age_composition_trend()`), selected years:

| Year | Morocco 15-39% | Algeria 15-39% |
|---|---|---|
| 2002 | 81.9% | 87.4% |
| 2010 | 75.7% | 65.7% |
| 2017 | 58.8% | 42.0% |
| 2019 | 57.4% | 42.9% |
| 2022 | 56.3% | 48.6% |
| 2024 | 57.0% | 53.7% |
| 2025 | 57.6% | 60.2% |

Morocco's population has been steadily **aging in place** since 2002 (a long-settled
community). Algeria's followed the same aging trajectory even more sharply through
2017-2018 (bottoming at 41.2% aged 15-39 that year), then **rejuvenated** from a fresh wave
of arrivals starting ~2018-2019 (back to 53.7% by 2024, 60.2% by 2025) — timing that
roughly coincides with the period T41 found the rate divergence emerging in. By 2024 the
two countries' shares are close (57.0% vs 53.7%, Algeria still slightly older-skewed that
specific year) — much closer than in 2010 (75.7% vs 65.7%) or 2017 (58.8% vs 42.0%) — yet
2024 is exactly the year the rate GAP is largest. If age composition were driving the gap,
the gap should track the age-share gap; instead the age-share gap shrank while the rate gap
grew. This is consistent with, and explains mechanically why, the SIR-ratio test above
shows age-adjustment widening rather than narrowing the divergence.

## H1 — is it a denominator undercount (differential legal access → more unregistered Algerians)?

**Hypothesis**: if Algerians historically had harder legal pathways into documented
residence/work than Moroccans, more of the true Algerian population in Spain may sit
outside official population statistics (Padrón/Eurostat stock), inflating the *computed*
per-capita rate purely from an undercounted denominator — not more actual crime.

**Research finding, real and citable**: Spain has a documented, decades-long asymmetry in
formal legal-migration pathways between the two countries.
- **Morocco**: a 1996 bilateral agreement on residence and work permits
  ([BOE-A-1996-12097](https://www.boe.es/diario_boe/txt.php?id=BOE-A-1996-12097)), a 2001
  labor agreement
  ([BOE-A-2001-17764](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2001-17764)), and an
  ongoing seasonal-worker recruitment program (Gestión Colectiva de Contrataciones en
  Origen, GECCO) run through Spain's labor ministry, structured specifically around
  agricultural campaign hiring. Morocco is listed among the countries Spain has active
  "convenios de flujos migratorios laborales" (labor migration flow agreements) with,
  per the Ministerio de Inclusión, Seguridad Social y Migraciones
  ([source](https://www.inclusion.gob.es/en/web/migraciones/convenios-de-flujos-migratorios-laborales)).
- **Algeria**: no equivalent labor-migration-flow agreement exists. What Spain and Algeria
  have signed are economic/fiscal instruments — a Double Taxation Avoidance Convention
  (2002, in force 2005) and an Agreement for the Reciprocal Protection of Investments
  (1994) — and readmission agreements governing the *return* of irregular migrants, not
  their legal entry. Algeria is absent from Spain's labor-migration-flow-agreement list.

This is a real, citable structural asymmetry: Morocco has had institutionalized, renewable
legal pathways into the Spanish labor market for ~30 years; Algeria has not. It is a
plausible **mechanism** for H1, but not itself a quantified undercount.

**What cannot be quantified from repo data**: no estimate of irregular/undocumented
migrant stock exists in this project (SPEC.md's N4/N11 backlog threads are open, status
`.`) — there is no way to directly measure "how many more unregistered Algerians are
there really." H1 remains a plausible, evidence-backed mechanism, not a measured effect.

## H2 — did the 2026 regularization process disproportionately surface Algerians? (N20)

Spain ran an extraordinary regularization process (April 16 - June 30, 2026) for migrants
already resident before January 1, 2026; 1,174,978 applications were received, of which
822,000 had provisional residence/work permits granted as of the ~30%-remaining-to-process
point in late July 2026
([Moncloa, 2 Jul 2026](https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/inclusion/Paginas/2026/020726-balance-regularizacion-extraordinaria.aspx);
[Moncloa summary, 24 Jul 2026](https://www.moncloa.com/2026/07/24/regularizacion-extraordinaria-migrantes-822000-3404704/)).

**Correction to an earlier pass of this report**: an initial search only surfaced the
top-5-named ranking (Colombia/Morocco/Venezuela/Peru/Honduras) plus continent aggregates,
with Algeria folded into an unresolved "Africa minus Morocco" residual. A fuller ranking
does exist and names Algeria individually — found by fetching the primary news article
directly rather than trusting a search engine's own synthesized summary (which, on
verification, had fabricated a plausible-looking but unsourced extended list; discarded).

**Full nationality breakdown of the 1,174,978 applications**, quoted directly from
[El Español, 2 Jul 2026](https://www.elespanol.com/espana/20260702/colombianos-marroquies-venezolanos-ranking-regularizacion-total-solicitudes/1003744307730_0.html)
(citing provisional Ministry figures, corroborated for the top-5 by the
[official Moncloa release](https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/inclusion/Paginas/2026/020726-balance-regularizacion-extraordinaria.aspx)):
Colombia 25.9%, Morocco 13.3%, Venezuela 11.8%, Peru 8.8%, Honduras 4.8%, Paraguay 3.8%,
**Algeria 3.4%**, Senegal 2.9%, Pakistan 2.5%, Argentina 2.3%, other 20.5% — sums to
100.0% exactly, an internal-consistency check that this is a real, coherent table, not a
partial quote. Stored with full provenance in `data/raw/regularization_2026.csv`.

**Comparing to existing registered population share** (this project's own data,
`migration_spain.csv`, 2025 Eurostat stock, 50-nationality cross, V6 denominator stated):

| Country | Applications | % of applications | Existing 2025 stock | % of registered stock | Ratio (applications ÷ stock share) |
|---|---|---|---|---|---|
| Morocco | 156,272 | 13.3% | 968,999 | 14.8% | **0.90x** |
| Algeria | 39,949 | 3.4% | 89,592 | 1.4% | **2.49x** |

Morocco's regularization-application share tracks its existing registered population share
closely (slightly *below* proportional) — no evidence of a large hidden Moroccan
population, despite Morocco having the *stronger* institutionalized legal pathway per H1.
**Algeria's application share is ~2.5x its existing registered population share** — a real,
disproportionate signal in exactly the direction H1 predicts: a nationality with weaker
legal pathways into documented status shows up disproportionately in the pool of people who
needed this regularization process to formalize their situation. This is now a genuine,
though not conclusive, quantitative data point supporting H1 — not just a plausible
mechanism. (Caveat: this is one regularization process, self-selected among people who met
the "resident before 2026-01-01" eligibility bar and chose to apply; it is not a direct
census of the full irregular population, and 20.5% of applications remain in an
unattributed "other" bucket.) N20 in SPEC.md updated to reflect this finding.

### Sensitivity scenario: how much would this shrink the peligrosity rate? (T84)

Direct follow-up: if the *entire* regularization-application pool for a nationality (a)
had already been present in Spain throughout the 2019-2024 crime-data window, just
uncounted in official stock, (b) were 100% aged 15-59, and (c) split male/female in that
nationality's own real registered sex ratio (a genuine estimate, not an aggressive
assumption — see the actual per-country splits used below) — an explicit **upper bound**,
not a best estimate, per assumptions (a)/(b) — how much would the computed peligrosity
rate fall? `src/crime/compute_regularization_sensitivity.py` →
`data/processed/regularization_sensitivity_test.csv` + chart
(`data/processed/regularization_sensitivity.png`), run for all 10 nationalities
individually named in the regularization breakdown (§H2):

**Male/female split used** (each nationality's own 2024 registered 15-59 sex ratio,
applied to its full regularization-application estimate — not a flat 50/50):

| Country | Male 15-59 (2024) | Female 15-59 (2024) | Male share | Applications (est.) | Added to male denom. |
|---|---|---|---|---|---|
| Senegal | 62,039 | 14,428 | 81.1% | 34,074 | +27,645 |
| Pakistan | 61,492 | 25,412 | 70.8% | 29,374 | +20,785 |
| Algeria | 37,957 | 19,154 | 66.5% | 39,949 | +26,551 |
| Morocco | 413,895 | 280,408 | 59.6% | 156,272 | +93,158 |
| Argentina | 53,526 | 55,165 | 49.2% | 27,024 | +13,308 |
| Colombia | 218,022 | 256,921 | 45.9% | 304,219 | +139,651 |
| Venezuela | 113,963 | 133,149 | 46.1% | 138,647 | +63,941 |
| Peru | 76,951 | 94,765 | 44.8% | 103,398 | +46,336 |
| Paraguay | 36,318 | 61,924 | 37.0% | 44,649 | +16,506 |
| Honduras | 43,997 | 95,246 | 31.6% | 56,399 | +17,821 |

**Denominator/rate effect, latest available year** (2024, except Pakistan 2022 — it didn't
make MIR's top-N cutoff in 2023/2024, see caveat below), sorted by rate reduction:

| Country | Denom. increase | Rate: original → over-corrected |
|---|---|---|
| **Algeria** | **+69.9%** | 634.9 → 373.6 /100k (**−41.2%**) |
| Colombia | +64.1% | 281.6 → 171.7 /100k (−39.0%) |
| Peru | +60.2% | 371.7 → 232.0 /100k (−37.6%) |
| Venezuela | +56.1% | 170.2 → 109.0 /100k (−35.9%) |
| Paraguay | +45.4% | 264.3 → 181.7 /100k (−31.2%) |
| Senegal | +44.6% | 270.8 → 187.3 /100k (−30.8%) |
| Honduras | +40.5% | 347.8 → 247.5 /100k (−28.8%) |
| Pakistan (2022) | +37.4% | 179.8 → 130.9 /100k (−27.2%) |
| Argentina | +24.9% | 143.9 → 115.2 /100k (−19.9%) |
| **Morocco** | **+22.5%** | 260.9 → 213.0 /100k (**−18.4%**) |

**Algeria shows the single largest correction of all 10 nationalities; Morocco shows the
smallest** — not just an Algeria-vs-Morocco artifact, Algeria and Morocco sit at opposite
ends of the entire distribution. This directly visualizes H1's mechanism: Algeria's small
existing registered base means the same regularization pool nearly doubles its denominator,
while Morocco's much larger existing base only grows ~23%. **But even at this maximal
correction, Algeria's 2024 rate is still ~1.75x Morocco's** (373.6 vs 213.0/100k), down from
2.43x uncorrected — narrowed substantially, not eliminated. The true correction is smaller
than this upper bound in reality (not every applicant arrived by 2019, not all are 15-59),
so the real gap sits somewhere between the original and over-corrected figures — but even
the extreme end leaves a real residual gap between Algeria and Morocco unexplained by this
mechanism alone.

**Coverage caveat**: Senegal/Paraguay/Argentina/Pakistan only have MIR perpetrator data for
1-3 of the 5 years (they didn't make every year's top-N reporting cutoff) — smaller sample
for those rows, not missing/fabricated data; years without MIR data are simply absent from
the CSV rather than zero-filled.

## Exploratory: does an offense-subtype signal exist for the "Africa" nationality group? (T78)

The user asked whether INE's convicted-offender data (finer offense-subtype detail,
region-level nationality only) could be cross-referenced against MIR's investigated data
(country-level nationality, no subtype detail) to approximate whether a specific offense
subtype skews by nationality. `src/crime/analyze_offense_subtype_funnel_triangulation.py`
→ `data/processed/offense_subtype_funnel_triangulation.csv` builds this comparison, with
two limitations that make it exploratory only, not resolving:

1. **Funnel-stage mismatch** (same as H3's caveat): convicted (INE) vs.
   investigated/identified (MIR) are different stages of denuncia → investigación →
   imputación → condena, each with its own attrition that need not be uniform across
   nationality or subtype.
2. **Granularity mismatch**: INE 28716 stops at "Africa" (no Morocco/Algeria split); MIR's
   within-Africa country shares (Morocco 67.7%→59.8% of Africa's MIR perpetrators
   2019→2024; Algeria 8.5%→13.1% over the same span — Algeria's share of Africa's cases
   has been rising, consistent with T41's own Test C finding) can at best be used as a
   weak proxy for how much of Africa's convicted mix either country might represent, not a
   real breakdown.

Observed: Africa's convicted-subtype mix shifted sharply after 2022 (abusos_sexuales share
fell from ~41% in 2021-2022 to ~20-27% in 2023-2024, while agresión sexual/violación-type
categories rose correspondingly) — this lines up with the LO 10/2022 "Solo sí es sí" reform,
which merged the legal categories of "abuso" and "agresión" sexual (C3's documented
definition break), so this shift is very likely a **legal reclassification artifact**, not
a real change in offense composition, and should not be read as a nationality-linked
subtype signal. No reliable Morocco/Algeria-specific offense-subtype conclusion can be
drawn from currently available data.

## Summary

| Hypothesis | Verdict | Confidence |
|---|---|---|
| H3 (age composition explains the gap) | **Not supported** — age-adjustment widens, not narrows, the gap in every year tested; population age-shares converged exactly when the rate gap was largest | Medium (real data, but funnel-stage-mismatched reference curve) |
| H1 (denominator undercount via differential legal access) | **Plausible mechanism WITH a supporting quantitative signal** — real, citable asymmetry in bilateral legal-migration pathways (Morocco has them since 1996/2001+GECCO, Algeria doesn't); Algeria's 2026 regularization-application share is ~2.5x its existing registered-population share (vs. Morocco's ~0.9x) — consistent with, though not proof of, a larger true undercount for Algeria | Medium (real, sourced applications data; still not a direct undocumented-population census) |
| H2 (2026 regularization disproportionately surfaced Algerians) | **Yes, disproportionately, by a real margin** — Algeria's application share (3.4%) is ~2.5x its registered-population share (1.4%); Morocco's (13.3%) roughly tracks its own (14.8%). Sensitivity test (T84): even the maximal over-corrected denominator narrows but does not eliminate Algeria's 2024 rate excess over Morocco (2.43x → 1.75x) | Medium (real official data, one process, self-selected applicant pool, 20.5% unattributed residual) |
| Offense-subtype signal (exploratory) | **No reliable signal extractable** — confounded by a 2022 legal-reclassification break and funnel/granularity mismatches | Low (exploratory only) |

H3 (the strongest a priori candidate) points the *opposite* direction once tested with real
data — age-adjustment widens, not narrows, the gap. H1/H2 together now provide a real,
though partial, explanation: Algeria shows a disproportionately large "surfacing" in the
2026 regularization process relative to its official population, consistent with a
meaningfully undercounted denominator — but even the most generous correction leaves
roughly half the original gap (2.43x → 1.75x) unexplained. The residual gap is real,
statistically significant (per T41), and not fully accounted for by any mechanism tested
here. This is reported as a partially-explained finding, not forced into either "fully
resolved" or "fully mysterious" — consistent with this project's C9 (no fabricated point
estimates) and the "association only" (V9) discipline used throughout.

## Data/code produced by this report

- `src/crime/parse_ine_tabla28857.py` → `data/processed/ine_condenados_28857_age_nationality.csv` (T76)
- `src/crime/compute_age_standardized_rate.py` → `data/processed/age_standardized_rate_test.csv`,
  `data/processed/age_standardized_dz_ma_ratio.csv` (T77)
- `src/migration/build_dashboard_data.py`: `_country_age_pyramid()`, `_working_age_composition_trend()`
  → `docs/data/migration.json` keys `stock_age_pyramid_dz_ma`, `dz_ma_working_age_trend`; dashboard
  panels `mi-age-pyramid-dz-ma`, `mi-dz-ma-age-trend` (T76)
- `src/crime/analyze_offense_subtype_funnel_triangulation.py` → `data/processed/offense_subtype_funnel_triangulation.csv` (T78)
- `data/raw/regularization_2026.csv` — 2026 regularization application share by nationality, sourced (new)
- `src/crime/compute_regularization_sensitivity.py` → `data/processed/regularization_sensitivity_test.csv`,
  `data/processed/regularization_sensitivity.png` (T84)
- B39 fix to `src/crime/analyze_cohort_crime_rate.py` (ROOT path + stock-series regression)
