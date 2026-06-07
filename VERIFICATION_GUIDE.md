# Data Verification Guide

Consolidates the former `SEXUAL_VIOLENCE_VERIFICATION.md`, `QUICK_VERIFY_SEXUAL_VIOLENCE.md`,
and `MORTALITY_MIGRATION_VERIFICATION_GUIDE.md` into one reference, organized by data domain.

All branches referenced below (`spain-migration-data`, `spain-mortality-analysis`,
`secondary-sources-spanish-analyses`, `violence-statistics-spain`) are now **merged into `main`**
— the "pending verification" status from the original guides is historical context, not an
open task. Use this guide to spot-check row values against primary sources, not to gate a merge.

---

## Using the Dashboard Data Viewer

`docs/index.html` includes a **Data Viewer / Raw Data Verification** section:

1. Open `docs/index.html` in a browser
2. Pick the relevant data category button (e.g. "📋 Sexual Violence Data")
3. A modal opens showing all rows for that category: Year, Type/Metric, Value, Confidence,
   **Source → clickable link 📎**, and Notes
4. Click a source link to jump directly to the original PDF/table and cross-check the value
5. Use the search box to filter by year, type, or source

### Confidence badge meaning

- 🟢 **High** — primary government/official source, direct figure (no computation)
- 🟡 **Medium** — primary source requiring minor computation, or reputable secondary source
- 🟠 **Low** — ambiguous, secondary, or inferred
- 🔴 **Unverified** — from a prior AI conversation; cross-check required before use (see C9 in SPEC.md)

---

## 1. Sexual Violence Data (`data/raw/violence_spain.csv`)

### Sources & where to find data

**MIR — Ministerio del Interior** (police-reported sexual crimes, 2000–2024):

| Years | Location |
|---|---|
| 2024 | [Informe 2024 PDF](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf) — Table 1: total crimes by type |
| 2023 | [Informe 2023 PDF](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2023/INFORME-DELITOS-CONTRA-LA-LIBERTAD-SEXUAL-2023.pdf) — Table 1 |
| 2022 | [Informe 2022 PDF](https://www.interior.gob.es/opencms/pdf/prensa/balances-e-informes/2022/INFORME-DELITOS-CONTRA-LA-LIBERTAD-SEXUAL-2022.pdf) — series-break note (LO 10/2022) |
| 2000–2021 | [Anuarios Estadísticos](https://www.interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/anuario-estadistico-del-ministerio-del-interior/) — chapter "Criminalidad" → sexual crimes |

Key tables inside each Informe: **Table 1** totals by category, **Table 2** victims (sex/age),
**Table 3** perpetrators (sex), **Table 4** clearance rates. (See also
`data/sources/mir_informes_delitos_sexuales.md` for the full index incl. direct PDF URLs back to 2000,
and the nationality-breakdown gap that T26 must fill.)

**Delegación del Gobierno** (partner-violence femicide registry & Macroencuesta survey):

| Type | Location |
|---|---|
| Femicide registry | https://violenciagenero.igualdad.gob.es/violenciaencifras/victimasmortales/fichamujeres/ — series 2003–2024 |
| Macroencuesta 2024 | https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta2024/ — Table 2.1 lifetime prevalence |
| Macroencuesta 2019 | https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta2015/Macroencuesta2019/ |
| Macroencuesta 2015 | https://violenciagenero.igualdad.gob.es/violenciaencifras/estudios/colecciones/libro-22-macroencuesta/ |

### Spot-check values (known-good as of last verification pass)

- **2024 total sexual crimes**: 22,846 — MIR Informe 2024, Table 1, row "Total"
- **2024 rape (violaciones, Anuario headline)**: ~5,223 (≈22.86% of total) — see B6 caveat below
- **2024 victims**: 22,778 total, 19,518 female (85.69%), 41.2% under 18 — Tables 2–3
- **Macroencuesta 2024**: "Violencia sexual" lifetime prevalence ≈ 7% (Table 2.1) — NOT comparable to 2019 wave (methodology changed)

### Known issue — B6: two incompatible "violaciones" series

MIR **Anuario** headline (~5,000/yr) vs MIR **Informe** subcategory (~1,200/yr) for the same years:

| Source | 2024 | 2019 | 2017 |
|---|---|---|---|
| Anuario headline (Art.179 + Art.181 — broad) | 5,223 | 5,453 | 3,716 |
| Informe subcategory (Art.179 only — narrow) | ~1,200 | 1,520 | 1,118 |

**We use the Anuario (broader) series** — more consistent pre-2022, but note it spans both
agresión and abuso. When verifying a "violaciones" row, check which series it cites and don't
mix them. Full analysis: `data/sources/fuentes_secundarias_analisis_espana.md` § 20.

### Known issue — LO 10/2022 series break

On **6 September 2022**, "abuso sexual" (no force) was merged into "agresión sexual"
(force/coercion) by [LO 10/2022 "Solo sí es sí"](https://www.boe.es/diario_oficial/pdf/BOE-A-2022-14630.pdf).
Pre- vs post-break totals are **not directly comparable**; 2022 itself straddles the change.
Verify against the MIR Informe 2022 methodology section.

### Verification workflow (per row)

1. Note the value shown in the dashboard
2. Click the source link 📎 and locate the table (usually Table 1 or an appendix)
3. Cross-check: exact match → confidence justified; ±1–2% → likely rounding (medium-high);
   >5% → flag as discrepancy in SPEC.md §B
4. Note caveats: series break 2022, pre-2012 territorial exclusions (×1.3–1.5 multiplier needed
   to estimate national totals), Macroencuesta methodology changes

### Checklist

- [ ] Spot-check 3–5 random years against the linked Informe/Anuario PDF
- [ ] Verify 2024 figures against Informe 2024 Table 1 exactly
- [ ] Verify victim percentages sum correctly (female + male + unknown ≈ 100%)
- [ ] B6 and LO 10/2022 notes present wherever relevant rows appear
- [ ] Record any new discrepancy in SPEC.md §B

---

## 2. Migration Data (`data/raw/migration_spain.csv`)

391 rows, 2000–2025: flows, stocks, and Social-Security-affiliation series by year/sex/age/origin/nationality.
Full source documentation: `data/sources/migracion_espana.md`.

### Sources & verification method

| Data category | Primary source | Verification method |
|---|---|---|
| Immigration flows 2000–2024 | INE — Estadística de Migraciones y Cambios de Residencia (EMCR), [table 24290](https://www.ine.es/jaxiT3/Tabla.htm?t=24290&L=0) | Spot-check 5–10 random rows by year/sex/age/nationality |
| Historical flows 2000–2007 | INE — Estadística de Variaciones Residenciales (EVR), [methodology](https://www.ine.es/daco/daco42/migracion/notaevr.htm) | Note breaks in 2004, 2006, and the 2008 EVR→EMCR transition |
| Foreign-nationality stock 2000–2025 | INE — Padrón Continuo / ECP, [table 36825](https://www.ine.es/jaxiT3/Tabla.htm?t=36825&L=0) (by nationality × age × sex, 1 Jan snapshots) | Verify 2024 total matches published Padrón figure |
| Top-10 origin nationalities | INE tables 24293 / 24295 | Spot-check 2024 inflow totals match dashboard row totals |
| Sex & age breakdowns | INE table 24312 (by CCAA, sex, age) | Cross-check female + male = total for 2024 |
| Social Security affiliation | MISSM/OPI — Afiliación de Extranjeros, https://www.inclusion.gob.es/web/opi/estadisticas/catalogo/afiliacion | Note known incomplete coverage (flagged in source doc) |

### Known caveats (see `data/sources/migracion_espana.md` for detail)

- **2008 break**: EVR → EMCR methodology change — pre/post-2008 flow series not directly comparable
- **2021 break**: Padrón → ECP (Estadística Continua de Población) — stock series break
- **Brexit reclassification**: UK nationals shift between "EU" and "non-EU" groupings around 2020–2021

### Checklist

- [ ] Cross-check 5–10 random rows against `data/sources/migracion_espana.md`
- [ ] Verify 2024 foreign-nationality stock total matches INE Padrón
- [ ] Verify sex-split sums = published totals, 2008–2024
- [ ] Confirm 2008 and 2021 series-break notes are present on the affected rows

---

## 3. Mortality & Population Data

Files: `data/processed/population_spain_midyear_5yr.csv` (2000–2025, by age/sex),
`data/processed/mortality_spain_ine_ecm.csv` (~198k rows, 2000–2024 by age × sex × cause),
`data/processed/mortality_rates*.csv` (derived).

| Data category | Primary source | Verification method |
|---|---|---|
| Female population by age, 2000–2025 | INE — Estimaciones de Población Actual, [table 56934](https://www.ine.es/jaxiT3/Tabla.htm?t=56934) (mid-year/1 July, 5-yr age bands) | **Key check**: 2024 female total = 24,881,624 (exact INE match ✅) |
| All-cause mortality by age × sex × cause | INE — Defunciones según la Causa de Muerte / ECM, [table 7947](https://www.ine.es/jaxiT3/Tabla.htm?t=7947); JSON API: https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/7947?nult=25&tip=A | 2000–2024, ICD-10 reduced list (120 causes) × 22 age groups |
| Mortality rates (per 100k) | Derived: (deaths ÷ population) × 100,000 | **Key check**: 2024 all-cause female = (189,987 ÷ 24,881,624) × 100,000 ≈ 763/100k |
| Cause-of-death chapters | INE ECM reduced-list mapping, ICD-10 chapters I–XX | See `data/sources/ine_causas_muerte.md`; chapter XX = "causas externas" (accidents, homicide, suicide) |

### Checklist

- [ ] Check 2024 female population total = 24,881,624 exactly
- [ ] Cross-check 3–5 random 2024 rows (age × sex × cause × count) against the INE ECM online table
- [ ] Verify rate computation: count ÷ population × 100,000
