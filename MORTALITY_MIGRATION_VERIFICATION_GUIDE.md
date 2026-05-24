# Manual Verification Guide

## Branch 2: Migration Data (`claude/spain-migration-data-PsIYr`)

**File to verify:** `data/raw/migration_spain.csv` (390 rows)

### Sources & Sections to Check:

| Data Category | Primary Source | Verification Method |
|---|---|---|
| **Immigration flows 2000–2024** | INE — Estadística de Migraciones y Cambios de Residencia (EMCR) | Table 24290: https://www.ine.es/jaxiT3/Tabla.htm?t=24290&L=0 — Verify 5–10 random rows match by year, sex, age, nationality |
| **Historical flows 2000–2007** | INE — Estadística de Variaciones Residenciales (EVR) | EVR methodology: https://www.ine.es/daco/daco42/migracion/notaevr.htm — Note changes in 2004, 2006 |
| **Foreign-nationality stock 2000–2025** | INE — Padrón Continuo / Estadística Continua de Población | Table 36825 (by nationality, age, sex): https://www.ine.es/jaxiT3/Tabla.htm?t=36825&L=0 — 1 Jan snapshots |
| **Top-10 origin nationalities intake** | INE Table 24293 or 24295 | Spot-check 2024 total inflow matches dashboard row totals |
| **Sex & age breakdowns** | INE Table 24312 (by CCAA, sex, age) | Cross-check 2024 female + male sum = total in CSV |
| **Social Security affiliation** | MISSM/OPI — Afiliación de Extranjeros | https://www.inclusion.gob.es/web/opi/estadisticas/catalogo/afiliacion — See branch for incomplete coverage |

---

## Branch 3: Mortality Data (`claude/spain-mortality-analysis-nYODb`)

**Files to verify:**
- `data/processed/population_spain_midyear_5yr.csv` (2000–2025, by age/sex)
- `data/processed/mortality_spain_ine_ecm.csv` (198k rows, 2000–2024 by age × sex × cause)
- `data/processed/mortality_rates*.csv` (derived rate files)

### Sources & Sections to Check:

| Data Category | Primary Source | Verification Method |
|---|---|---|
| **Female population by age, 2000–2025** | INE — Estimaciones de Población Actual (table 56934) | https://www.ine.es/jaxiT3/Tabla.htm?t=56934 — Mid-year (July 1) estimates, 5-yr age bands. **Key check:** 2024 female total = 24,881,624 (exact INE match ✅) |
| **All-cause mortality by age × sex × cause** | INE — Defunciones según la Causa de Muerte / ECM (table 7947) | https://www.ine.es/jaxiT3/Tabla.htm?t=7947 — 2000–2024, ICD-10 reduced list (120 causes), 22 age groups. Data pull via JSON API: https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/7947?nult=25&tip=A |
| **Mortality rates (per 100k)** | Derived from population + mortality data | Formula: (deaths by age × year / population by age × year) × 100,000. **Key check:** 2024 all-cause female = (189,987 deaths / 24,881,624 pop) × 100,000 = ~763/100k |
| **Cause-of-death chapters** | INE ECM reduced-list mapping | ICD-10 chapters I–XX: see data/sources/ine_causas_muerte.md § ICD-10 chapter map. Note: Chapter XX = "Causas externas" (accidents, homicide, suicide). |

---

## Quick Verification Checklist

### Migration (Branch 2)
- [ ] Open `data/raw/migration_spain.csv`
- [ ] Cross-check 5–10 random rows against `data/sources/migracion_espana.md`
- [ ] Verify 2024 foreign-nationality stock total matches INE Padrón
- [ ] Verify sex-split sums = published totals (2008–2024)

### Mortality (Branch 3)
- [ ] Open `data/processed/population_spain_midyear_5yr.csv`
- [ ] Check 2024 female total = 24,881,624 (exact match = ✅)
- [ ] Open `data/processed/mortality_spain_ine_ecm.csv`
- [ ] Cross-check 3–5 random 2024 rows (age × sex × cause × count) against INE ECM online table
- [ ] Verify rate computation: count / population × 100,000

---

## Using the HTML Dashboard for Verification

The updated dashboard at `docs/index.html` now includes a **Data Viewer** button:

1. Click **"Open Data Viewer"** button (below the charts)
2. A modal opens showing all rows from `data/raw/violence_spain.csv`
3. Each row displays:
   - Year, Type, Value, Confidence level
   - **Source name as a clickable link 📎** — jump directly to the source URL
   - Notes explaining the data
4. Use the **search box** to filter by year, violence type, or source

### Confidence Badge Colors

- 🟢 **High** — Primary government/official source, direct data (no computation)
- 🟡 **Medium** — Primary source requiring minor computation or reputable secondary source
- 🟠 **Low** — Ambiguous, secondary, or inferred
- 🔴 **Unverified** — From prior AI conversation; cross-check required before use

---

## Status

**Merged (✅):**
- Branch 1: `claude/secondary-sources-spanish-analyses` — B6 bug resolved, secondary analyses added
- Branch 4: `claude/violence-statistics-spain-Dmqy0` — Already merged

**Pending Manual Verification (⏳):**
- Branch 2: `claude/spain-migration-data-PsIYr` — 390 migration rows
- Branch 3: `claude/spain-mortality-analysis-nYODb` — 198k mortality rows + population data

**Next Steps:**
1. Open `docs/index.html` in a browser
2. Click "Open Data Viewer" button
3. For each row you want to verify, click the source link 📎
4. Cross-check against the linked INE/MITES tables (see sources above)
5. Once verified, merge with:
```bash
git merge remotes/origin/claude/spain-migration-data-PsIYr -m "Manual verification complete — branch 2 migration data verified"
git merge remotes/origin/claude/spain-mortality-analysis-nYODb -m "Manual verification complete — branch 3 mortality data verified"
```
