# Algeria/Morocco peligrosity divergence — why is Algeria's rate higher and rising while Morocco's is stable?

Synthesizes T41's cohort-tenure tests with three follow-up hypotheses (T76-T79, N20)
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

**Population-side confirmation (T76)** — Morocco vs Algeria age pyramid
(`docs/index.html` panel `mi-age-pyramid-dz-ma`) and working-age composition trend
(panel `mi-dz-ma-age-trend`, `data/processed` via `src/migration/build_dashboard_data.py`'s
new `_working_age_composition_trend()`) show why: Morocco's population has been steadily
**aging in place** since 2002 (% of male stock aged 15-39 fell from 81.9% in 2002 to 57.4%
by 2024 — a long-settled community). Algeria's population followed the same aging
trajectory even more sharply through 2017-2018 (bottoming at ~41-42% aged 15-39), then
**rejuvenated sharply** from a fresh wave of arrivals starting ~2018-2019 (rising back to
57.0% by 2024, 60.2% by 2025) — timing that roughly coincides with the period T41 already
found the rate divergence emerging in. But by **2023-2024, the two countries' age shares
had converged to nearly identical values** (Morocco 57.4%/56.6%, Algeria 57.6%/57.0%) —
exactly the period where the rate GAP is largest. If age composition were driving the
gap, it should be smallest when the two populations' age profiles are most similar; the
opposite is observed. This is consistent with, and explains mechanically why, the SIR-ratio
test above shows age-adjustment widening rather than narrowing the divergence.

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

**Official nationality breakdown of the 1,174,978 applications** (per the Moncloa press
release): Colombia 25.9%, **Morocco 13.3%**, Venezuela 11.8%, Peru 8.8%, Honduras 4.9%.
By continent: Latin America 66.7%, **Africa 22.9%**, Asia 8.3%. **Algeria is not named** —
its applications fall inside the residual "Africa minus Morocco" bucket
(22.9% − 13.3% = 9.6% of all applications, ≈112,800), shared with Senegal, Nigeria, Mali,
Ghana, Gambia, Guinea, and Equatorial Guinea (the other African nationalities tracked in
this project's `REGION_MAP`) — Algeria's individual share cannot be isolated from public
figures.

**Comparing to existing registered population share** (this project's own data,
`migration_spain.csv`, 2025 Eurostat stock, 50-nationality cross, V6 denominator stated):
Morocco is 968,999 of 6,560,766 (**14.8%**) of that cross; Algeria is 89,592 (**1.4%**).
Morocco's regularization-application share (13.3%) tracks its existing registered
population share (14.8%) closely — **no evidence of a large hidden Moroccan population
surfacing**, despite Morocco having the *stronger* institutionalized legal pathway per H1.
Algeria's true regularization share is bounded above by the 9.6% "other Africa" residual —
roughly 6-7x Algeria's 1.4% existing population share **if** the entire residual were
Algerian, which is implausible given seven other named nationalities compete for that same
bucket. **Inconclusive for Algeria specifically**: the published data does not break
Algeria out, so H1/H2 cannot be confirmed or ruled out from this process's results as
currently published. This is reported honestly as an open gap (per C9 — no fabricated
point estimate), not resolved. N20 in SPEC.md is set to `~` (searched, found real
aggregate/Morocco-specific data, but not an Algeria-specific figure) rather than left
silently unaddressed.

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
| H1 (denominator undercount via differential legal access) | **Plausible mechanism, unquantified** — real, citable asymmetry in bilateral legal-migration pathways (Morocco has them since 1996/2001+GECCO, Algeria doesn't), but no irregular-population estimate exists to size the effect | Low (mechanism sourced; magnitude unknown) |
| H2 (2026 regularization disproportionately surfaced Algerians) | **Inconclusive** — official data doesn't break out Algeria; Morocco's share tracks its existing population closely (no surprise there); Algeria's upper bound is suggestive but not confirmable | Low (real official data, but not granular enough) |
| Offense-subtype signal (exploratory) | **No reliable signal extractable** — confounded by a 2022 legal-reclassification break and funnel/granularity mismatches | Low (exploratory only) |

None of the three hypotheses currently resolve *why* Algeria's rate is rising faster than
Morocco's — if anything, H3 (the strongest a priori candidate) points the *opposite*
direction once tested with real data. The gap documented in T41 remains real,
statistically significant, and currently unexplained by population composition,
legal-pathway-driven undercounting (as far as it can be measured), or the 2026
regularization data as currently published. This is reported as an open finding, not
forced into a tidy explanation — consistent with this project's C9 (no fabricated point
estimates) and the "association only" (V9) discipline used throughout.

## Data/code produced by this report

- `src/crime/parse_ine_tabla28857.py` → `data/processed/ine_condenados_28857_age_nationality.csv` (T76)
- `src/crime/compute_age_standardized_rate.py` → `data/processed/age_standardized_rate_test.csv`,
  `data/processed/age_standardized_dz_ma_ratio.csv` (T77)
- `src/migration/build_dashboard_data.py`: `_country_age_pyramid()`, `_working_age_composition_trend()`
  → `docs/data/migration.json` keys `stock_age_pyramid_dz_ma`, `dz_ma_working_age_trend`; dashboard
  panels `mi-age-pyramid-dz-ma`, `mi-dz-ma-age-trend` (T76)
- `src/crime/analyze_offense_subtype_funnel_triangulation.py` → `data/processed/offense_subtype_funnel_triangulation.csv` (T78)
- B39 fix to `src/crime/analyze_cohort_crime_rate.py` (ROOT path + stock-series regression)
