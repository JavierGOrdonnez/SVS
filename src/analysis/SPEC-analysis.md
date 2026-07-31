# SPEC-analysis.md — analysis module

Part of the SVS spec. Top-level goal/shared constraints/invariants/roadmap/bug
log live in [`SPEC.md`](../../SPEC.md); this file owns §T tasks T5, T6, T8,
T9, T10, T12-T16, T32-T36, T52, T54, T56-T58 and this module's
domain-specific §V/§I content only — the cross-cutting probability/
regression/relationship/funnel/EU-comparative work, plus the shared
population denominator (`parse_ine_population.py`) and the dashboard
orchestrator itself.

---

## §I — Interfaces (analysis-specific)

```
file: data/raw/population_spain.csv                    → INE female population by age/year
file: data/processed/population_spain_estimates.csv    → full long-form population series (all Jan/Apr/Jul/Oct snapshots 1971-2025) (T6)
file: data/processed/population_spain_midyear_5yr.csv  → mid-year (July 1) population binned to 5yr age groups 2000-2025, shared denominator feeding mortality/feminicide/peligrosity rate computations (T6)
file: data/processed/population_spain_nationality.csv  → mid-year (July 1) Spanish/foreign/total nationality split, by sex × 17-band pyramid age scale + all-ages total, 2002-2025 — direct INE t.56936 source (V46), shared Spanish-population denominator feeding migration/feminicide/peligrosity/crime-trend/cohort rate computations, replacing the retired total-minus-foreign-stock derivation (T89, B44)
file: data/processed/rates.csv                         → derived incidence rates (generated)
file: data/processed/lifetable.csv                     → cumulative probability output (generated) (T8)
file: data/processed/covariate_data.csv                → political & immigration series (generated) (T10)
file: data/processed/relationship_structure.csv        → victim-aggressor relationship distribution + adjustment factors (T32, planned)
file: data/raw/mir_violence_sexual_2015-2019.csv       → "Informe evolución violencia mujer" 2015-2019 extract, 5 tables incl. victim-perp relationship + location of offense — available, untapped input for T32
file: data/raw/gbv_funnel.csv, data/processed/gbv_funnel_rates.csv → GBV non-sexual justice funnel (denuncias/diligencias/condenas) (T34, planned, later)
file: data/processed/aggression_profile_summary.txt    → four-dimension aggression profile (cifra oculta, known/unknown perp, relationship+location context, single/multi perp) (T52)
file: data/raw/eu_gbv_survey_{countries}.csv           → Eurostat EU-GBV survey `gbv_*` pull, ES + comparators (T56, planned)
cmd:  `uv run python src/analysis/parse_ine_population.py`   → INE table 56934 → `population_spain_estimates.csv`, `population_spain_midyear_5yr.csv` (T6)
cmd:  `uv run python src/analysis/parse_ine_population_nationality.py <csv_path>` → INE table 56936 CSV → `population_spain_nationality.csv` (T89)
cmd:  `python src/parsers/mir_violence_parser.py <pdf_path>`     → parse "Informe evolución violencia mujer" 2015-2019 PDF (5 tables incl. victim-perp relationship + location of offense), stdout summary only — available, untapped input for T32
cmd:  `python src/parsers/mir_violence_extractor.py <pdf_dir_or_file>` → extract same PDF's 5 tables → `data/raw/mir_violence_sexual_2015-2019.csv`
cmd:  `uv run python src/analysis/analyze_aggression_profile.py` → `violence_spain.csv` → `data/processed/aggression_profile_summary.txt` (T52)
cmd:  `python src/pipeline.py`                         → raw → processed (planned)
cmd:  `python src/lifetable.py`                        → rates → cumulative probs (planned, T8)
cmd:  `python src/regression.py`                       → covariate analysis (planned, T12)
file: `src/analysis/build_dashboard.py`                → orchestrator: calls each domain's `build_dashboard_data.build()` (feminicides, sexual_crimes, crime, migration, mortality) via `importlib` (all 5 modules share the filename `build_dashboard_data.py`, so a plain `import` would only bind the first one loaded) → `docs/data/*.json` (6 files) (T17,T23,T-mig-tab)
out:  reports/                                         → final write-ups & charts
html: docs/index.html (3 main tabs: violence, mortality, migration; `violence` nests 3 sub-tabs: sexual-crimes+Macroencuesta, feminicides, others [domestic-violence denuncias, all-cause homicide, EIGE sex/relationship breakdown, victim-perp matrix, homicide rate trend, confidence-distribution chart]) → interactive dashboard with rich visualizations
doc:  `data/sources/eige_fra_comparative.md`            → EIGE (Vilnius)/FRA (Vienna)/Eurostat EU-comparative GBV data — Eurostat EU-GBV survey `gbv_*` REST API (2024 wave, confirmed machine-readable, T56), EIGE administrative IPV/DV indicators (non-comparable across countries per EIGE's own caveat), EIGE femicide harmonisation (pilot phase, no operational cross-country count yet), FRA EU-MIDIS II country sheets (T57); enables Spain-vs-EU comparison using standardized methodology, complementing this repo's Spain-only series (macroencuesta/MIR/Delegación)
```

## §V — Invariants (analysis-specific)

V9: ∀ probability estimates → methodology section in report ! describe competing-risks model & assumptions.
V10: Covariate series ! cover same 2000–2025 range as violence series; gaps flagged.
V11: Dark-figure multipliers ! sourced from macroencuesta or published academic estimates; ⊥ invented.
V17: GBV justice-funnel rates ! keep administrative sources distinct — MIR police denuncias ≠ CGPJ judicial ≠ Fiscalía diligencias ≠ INE condenas; counts ⊥ divided across incompatible sources without a documented bridge.
V36: ∀ Spain-vs-other-EU-country comparison using EIGE/FRA/Eurostat GBV data → ! carry explicit caveats: (a) EIGE `genvio_int_adm_ipv` administrative indicators are ⊥ cross-country comparable per EIGE's own stated caveat (differing counting rules) — Spain-only confirmation data, not a comparator; (b) self-report prevalence differences (e.g. Sweden 48.2% vs Spain 28.6-30% lifetime IPV) reflect disclosure/normalization differences ("Nordic paradox"), not necessarily true-incidence differences — ⊥ read as "Spain does better"; (c) 2014 FRA survey vs 2024 EU-GBV survey is a methodology/question-redesign break, not a real trend — ⊥ chained into one time series (extends C3/V7's national-level definition-break rule to EU-survey wave changes).

## §T — Tasks (analysis)

| id | status | track | task | cites |
|---|---|---|---|---|
| T5 | ~ | A,B | Populate `violence_spain.csv` — Macroencuesta: 2015 & 2019 rows done (medium); 2024 wave rows 94–99 done (high; published 3 Dec 2025); 2011 & methodology-change caveats pending | V1,V3,V11 |
| T6 | x | A,B | Female (& male, total) population by 5-yr age group & year 2000–2025 (mid-year July 1) from INE table 56934 (Estimaciones de Población Actual) → `data/processed/population_spain_midyear_5yr.csv`. Source: 56934 also gives Jan/Apr/Jul/Oct 1971–2025 in `population_spain_estimates.csv`. Cross-check 2024 female: bin sum 24,881,624 = INE all-ages exact match. Script: `src/analysis/parse_ine_population.py` | V6,V10 |
| T8 | . | A | Build competing-risks life-table → `data/processed/lifetable.csv` — 1-yr, 5-yr, lifetime cumulative P for 2000-born cohort | V7,V9 |
| T9 | . | A | Dark-figure estimation: cross-validate police counts vs macroencuesta; compute multipliers per violence type | V11 |
| T10 | . | C | Collect covariate series: far-right vote share (Vox/PP far-right component) per year from CIS / electoral results | V10,C8 |
| T12 | . | C | Covariate regression: multivariate OLS + BSTS on violence-rate ~ covariates; report associations not causal claims | C8,V9 |
| T13 | . | C | Scenario projections: vary covariates ±10/20%, recompute expected rates | C8 |
| T89 | x | infra | New `parse_ine_population_nationality.py`: parse INE t.56936 CSV (Española/Extranjera/Total × 5yr age bands × sex × quarterly, 2002-2025) → `data/processed/population_spain_nationality.csv` (year,sex,age_group[0-4..80+,all],nationality,population_july1), July-1 rows only, age bands collapsed to the existing 17-band pyramid scale (`80-84`/`85-89`/`90 y más años`→`80+`), reusing `parse_ine_population.py`'s SEX_MAP/PERIOD_MONTH/parse_value/parse_periodo (T6). Fixes B44: replaces the total−foreign subtraction used repo-wide for Spanish-national population with INE's own directly-reported nationality series. Extended `data/sources/ine_poblacion_femicidios.md` (already pointed at t.31304 for this but never built it) with t.56936 as the implemented source + a derived-vs-primary comparison table. Test: `tests/test_parse_ine_population_nationality.py` | V46,V6 |
| T14 | . | A | Re-verify all `confidence=unverified` rows from prior AI conversation against primary sources | C9,V5 |
| T15 | . | infra | Write `reports/methodology.md` — definitions, legal changes, dark-figure approach, model spec; per-source extraction table + composition DAG (mermaid) + peligrosity/relationship/funnel definitions | V9,C3,C4 |
| T16 | . | infra | Write `reports/results.md` — probability estimates + CIs + scenario table | V9 |
| T32 | . | E | Extract victim–aggressor relationship structure — Macroencuesta (partner / known / stranger; ±penetration), MIR victim-perp matrix (2010–2012 + any newer), Delegación `relationship_status` → `data/processed/relationship_structure.csv` + victims-per-aggressor & repeat-victimization factors. | C5,V16 |
| T33 | . | E | Apply relationship adjustment — adjust §A victim risk & §D peligrosity using T32 factors; document each adjustment + source. | V16,V9 |
| T34 | . | G | *(later)* GBV non-sexual justice funnel — extract denuncias (CGPJ/MIR), diligencias (Fiscalía Memorias), condenas (INE Condenados/CGPJ), protection orders; compute reporting rate (vs Macroencuesta physical/psychological prevalence), prosecution rate, conviction rate → `data/raw/gbv_funnel.csv` + `data/processed/gbv_funnel_rates.csv`. | C5,V11,V17 |
| T35 | . | infra | Literature-evidence synthesis — from `fuentes_secundarias_analisis_espana.md` (29 sources) + 4 reference PDFs, extract each study's headline metrics + trace to primary source → `data/sources/literature_evidence.md` table; supplies dark-figure multipliers, victim-perp matrices, relationship priors as cross-checks. | C1,C15,V11 |
| T36 | . | infra | *(later)* Add composition/methodology diagram to `docs/index.html` (dashboard rendering of the extraction→metric DAG). | I.* |
| T52 | x | A,E | Aggression profile analysis — DONE: `src/analysis/analyze_aggression_profile.py`. Extracts four dimensions from `violence_spain.csv`: unreported-case (cifra oculta) rates by aggression type, known-vs-unknown perpetrators, context (relationship + location), single-vs-multiple perpetrators; writes `data/processed/aggression_profile_summary.txt`. Discovered as an unwired orphan during the T53 parser-consolidation cleanup. | V11,C5 |
| T54 | . | infra | *(later, backlog)* Consolidate near-duplicate analysis-script patterns — `compute_feminicide_rates.py`/`compute_mortality_rates.py` share an identical count÷population×100k-with-CI pattern (different sources); `build_dashboard_data.py`/`build_migration_dashboard_data.py` share an identical stdout-JS-emission pattern for `docs/index.html`. Documentation-only this round (see `data/PIPELINE.md`); code consolidation deferred. | — |
| T56 | . | C,infra | Pull Eurostat EU-GBV survey `gbv_*` aggregated-indicator API (2024 wave, joint Eurostat/FRA/EIGE) for ES + comparators (FR, DE, IT, SE, EU27_2020) — confirmed working REST JSON pull, no PDF parser needed (`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gbv_ipv_type?format=JSON&lang=en`; sibling tables per `gbv_sims` metadata cover non-partner violence, workplace sexual harassment, stalking, childhood violence). First genuinely cross-country-comparable Spain-vs-EU prevalence table this repo has. Must first pin the exact table/dimension filter for Spain's lifetime-IPV figure — two pulls in the research pass returned 28.6% vs 30.0% for the same nominal cell (`data/sources/eige_fra_comparative.md` §2.3/Open-followups) — before citing a headline number. Subject to V36's comparability caveats. → `data/raw/eu_gbv_survey_{countries}.csv` | C1,C15,V14,V36 |
| T57 | . | F | Extract EU-MIDIS II Spain country-sheet PDF (`fra-2019-eu-midis-ii-summary-results-country-sheet-spain_en.pdf`, URL confirmed live, plain WebFetch could not decode it — needs `pdftotext`/pdf skill) — resolves the specific violence/harassment-reporting-rate breakdown (88%/90%/72%, currently EU-aggregate only, `discurso_odio_inmigracion_espana.md` §2.3bis) to a Spain-specific figure; cross-check against REIC academic paper (Bermejo et al. 2021, *Revista Española de Investigación Criminológica* vol.19, Spain subsample N=1,563) which already yields 3 Spain-specific discrimination/profiling figures (35% antigypsism 5yr recall vs 27% EU avg; 21% perceived ethnic-profiling stops vs 8% EU avg; 12% reporting rate) at medium confidence pending primary-PDF cross-check. See `data/sources/eige_fra_comparative.md` §3 | C1,C15,V18 |
| T58 | . | C,infra | *(later, backlog)* Pull EIGE `genvio_int_adm_ipv` 13-indicator IPV/DV family for Spain + comparator countries, and the Gender Equality Index violence-domain composite scores (`dgs-p.eige.europa.eu/data/view?code=...`) for all EU-27 — EIGE's own documentation says the IPV/DV administrative indicators are explicitly NOT cross-country comparable (differing counting rules); pull anyway as a negative/caveat-establishing result quantifying how large that gap is in practice. Also resolves the open question of whether Spain is among the 12 EU countries with a calculated violence-domain composite score. Subject to V36(a). | C1,C15,V36 |

## Related bugs

B5, B16, B17, B20, B27, B44 — see `SPEC.md` §B for full text.
