# SPEC.md — SVS (Spain Violence Statistics)

---

## §G — Goal

Compute annual, 5-year & lifetime cumulative probability of rape/sexual-assault/femicide/homicide/non-sexual-violence for woman born 2000 ∈ Spain, holding 2025 conditions fixed. Extend: estimate partial effects of covariates (far-right vote share, immigration volume & composition) using 2000–2025 historical series.

---

## §C — Constraints

C1: All claimed statistics ! cite exact source + table/figure + year of publication.  
C2: Reported-crime data ≠ actual incidence; dark-figure correction ! attempted via survey cross-validation.  
C3: Definition of each offence ! documented per year — Spanish penal code changed materially in 2022 (LO 10/2022 "Solo sí es sí") & 2023 reform; pre/post comparability ⊥ assumed without explicit bridge.  
C4: "Femicide" in official data = intimate-partner/ex-partner homicide only (Delegación del Gobierno registry) ≠ all female homicides ≠ academic broad definition.  
C5: Macroencuesta (victimisation survey) ! used to bound dark figure; conducted irregularly (2011, 2015, 2019); interpolation between waves ? unreliable.  
C6: Age-specific rates ! used wherever available; aggregate rates ∈ fallback only.  
C7: ∀ probability estimates → competing-risks life-table, not naive annual-rate multiplication (events not independent across years).  
C8: Covariate regression = associative, ⊥ causal.  
C9: Prior AI model (Haiku) likely hallucinated point estimates without source verification → ∀ numbers from that conversation ! re-verified against primary sources before use.  
C10: Population denominator ! female population of Spain from INE Padrón; age-stratified where possible.  
C11: Ethnicity/nationality breakdowns sparse in official data; include when available, flag absence.  
C12: ∀ CSV rows ! have `confidence` ∈ {high, medium, low, unverified} — unverified rows ⊥ used in final estimates until confirmed.

---

## §I — Interfaces

```
file: data/raw/violence_spain.csv       → append-only raw data log
file: data/raw/population_spain.csv     → INE female population by age/year
file: data/processed/rates.csv          → derived incidence rates (generated)
file: data/processed/lifetable.csv      → cumulative probability output (generated)
file: data/processed/covariate_data.csv → political & immigration series (generated)
cmd:  `python src/pipeline.py`          → raw → processed
cmd:  `python src/lifetable.py`         → rates → cumulative probs
cmd:  `python src/regression.py`        → covariate analysis
out:  reports/                          → final write-ups & charts
```

---

## §V — Invariants

V1: ∀ row ∈ violence_spain.csv → `row_id`, `violence_type`, `year`, `value`, `unit`, `source_name`, `source_table`, `confidence` ! non-empty.  
V2: `confidence=high` → source is primary govt/official publication, value directly readable (not computed by prior AI).  
V3: `confidence=medium` → source is primary but value requires minor computation (e.g. rate from count + population) or source is reputable secondary.  
V4: `confidence=low` → source ambiguous, secondary, or value inferred.  
V5: `confidence=unverified` → value originates from prior AI conversation; ⊥ used in modelling until cross-checked.  
V6: ∀ rate computation → denominator ! stated (female population, female 15-49, etc.).  
V7: Definition-break years (2022 LO 10/2022, 2023 reform) ! flagged in `notes` for sexual-offence rows.  
V8: Femicide rows ! distinguish registry: `Delegación_Gobierno` (partner/ex only) vs `INE_MNP` (all female homicide) vs `CGPJ` (judicial).  
V9: ∀ probability estimates → methodology section in report ! describe competing-risks model & assumptions.  
V10: Covariate series ! cover same 2000–2025 range as violence series; gaps flagged.  
V11: Dark-figure multipliers ! sourced from macroencuesta or published academic estimates; ⊥ invented.

---

## §T — Tasks

| id | status | task | cites |
|---|---|---|---|
| T1 | x | Populate `violence_spain.csv` — femicide (partner/ex): Delegación del Gobierno 2003–2024; rows 1–22,90,91,104,105 complete; 2024=47 verified | V1,V2,V8 |
| T2 | ~ | Populate `violence_spain.csv` — all-cause homicide by sex: EIGE 2022 (rows 107–113), INE ECM 2023 rates+counts (rows 114–121), MIR Informe perp-sex breakdown (rows 122–124), feminicidio.net (125–126). INE ECM 2000–2024 full series now in `data/processed/mortality_spain_ine_ecm.csv` via T17. PENDING: MIR Anuario tables with sex breakdown. Source file: `data/sources/homicidio_espana.md` | V1,V2,V8 |
| T3 | ~ | Populate `violence_spain.csv` — sexual crimes MIR: 2022–2024 verified (rows 46–56,82–89); 2017–2021 medium; 2000–2016 unverified. BLOCKER: two incompatible violaciones series unresolved (B6) | V1,V2,V7 |
| T4 | . | Populate `violence_spain.csv` — non-sexual domestic violence denuncias: Ministerio del Interior / CGPJ 2000–2024 | V1,V2 |
| T5 | ~ | Populate `violence_spain.csv` — Macroencuesta: 2015 & 2019 rows done (medium); 2024 wave rows 94–99 done (high; published 3 Dec 2025); 2011 & methodology-change caveats pending | V1,V3,V11 |
| T6 | . | Populate `population_spain.csv` — INE female population by 5-yr age group & year 2000–2025 | V6,V10 |
| T7 | . | Compute age-specific annual incidence rates → `data/processed/rates.csv` | V3,V6 |
| T8 | . | Build competing-risks life-table → `data/processed/lifetable.csv` — 1-yr, 5-yr, lifetime cumulative P for 2000-born cohort | V7,V9 |
| T17 | x | All-cause mortality by age × sex × cause 2000–2024 from INE ECM table 7947 → `data/processed/mortality_spain_ine_ecm.csv` (198k rows) + summary CSVs. Source doc: `data/sources/ine_causas_muerte.md`. Scripts: `src/parse_ine_mortality.py`, `src/summarize_mortality.py` | V1,V2,V6 |
| T9 | . | Dark-figure estimation: cross-validate police counts vs macroencuesta; compute multipliers per violence type | V11 |
| T10 | . | Collect covariate series: far-right vote share (Vox/PP far-right component) per year from CIS / electoral results | V10,C8 |
| T11 | . | Collect covariate series: total immigration flow & stock by year, nationality, sex, age — INE/MITES | V10,C8 |
| T12 | . | Covariate regression: multivariate OLS + BSTS on violence-rate ~ covariates; report associations not causal claims | C8,V9 |
| T13 | . | Scenario projections: vary covariates ±10/20%, recompute expected rates | C8 |
| T14 | . | Re-verify all `confidence=unverified` rows from prior AI conversation against primary sources | C9,V5 |
| T15 | . | Write `reports/methodology.md` — definitions, legal changes, dark-figure approach, model spec | V9,C3,C4 |
| T16 | . | Write `reports/results.md` — probability estimates + CIs + scenario table | V9 |

---

## §B — Bugs

| id | date | cause | fix |
|---|---|---|---|
| B1 | 2026-05-20 | Haiku 2024 femicide count = 58; verified = 47 (−19%) | V2,V5 |
| B2 | 2026-05-20 | Haiku 2024 total sexual crimes = 21159; verified = 22846 (−7.4%) | V2,V5 |
| B3 | 2026-05-20 | Haiku 2024 agresiones sin penetración = 15953; verified = ~13673 (−14%) | V2,V5 |
| B4 | 2026-05-20 | Haiku 2023 total sexual crimes = 19981; verified = 21825 (−8.4%) | V2,V5 |
| B5 | 2026-05-20 | Haiku "62× cifra oculta" = invalid: divides annual denuncias by lifetime prevalence (incompatible units) | V11 |
| B6 | 2026-05-20 | Two incompatible violaciones series (MIR Anuario 3700–5453 vs Geo VG 1118–1520 for same years) — root cause unresolved | V3,V6 |
| B7 | 2026-05-20 | My arithmetic critique of INE Condenados 2024 was wrong: 90 violaciones is subcategory of 1389 not additive; Haiku figures confirmed correct | V2 |
