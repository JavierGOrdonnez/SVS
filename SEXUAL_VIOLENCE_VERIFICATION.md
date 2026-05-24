# Sexual Violence Data Verification Guide

## Quick Start

1. Open `docs/index.html` in a browser
2. Scroll down to "Raw Data Verification" section
3. Click **"📋 Sexual Violence Data"** button
4. A modal opens showing all sexual violence rows
5. Click **any source link 📎** to jump directly to the PDF/table
6. Verify the value matches what's in the source

---

## Data Structure

**Column headers in the viewer:**

| Column | Purpose |
|---|---|
| **Year** | Year of the data |
| **Violence Type** | Type of sexual violence (rape, assault, etc.) |
| **Value** | Count or percentage |
| **Confidence** | How certain we are of this data (high/medium/low/unverified) |
| **Source → Reference** | Clickable link 📎 to the original PDF/table |
| **Notes** | Caveats, definitions, or verification notes |

---

## Sources & Where to Find Data

### MIR — Ministerio del Interior

**Contains:** Police-reported sexual crimes 2000–2024

| Years | Location |
|---|---|
| **2024** | [Informe 2024 PDF](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf) — Table 1: Total crimes by type |
| **2023** | [Informe 2023 PDF](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2023/INFORME-DELITOS-CONTRA-LA-LIBERTAD-SEXUAL-2023.pdf) — Table 1: Delitos contra la libertad sexual |
| **2022** | [Informe 2022 PDF](https://www.interior.gob.es/opencms/pdf/prensa/balances-e-informes/2022/INFORME-DELITOS-CONTRA-LA-LIBERTAD-SEXUAL-2022.pdf) — Note: Series break 6 Sept 2022 (LO 10/2022) |
| **2000–2021** | [Anuarios Estadísticos](https://www.interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/anuario-estadistico-del-ministerio-del-interior/) — Chapter "Criminalidad" → Sexual Crimes |

**Key tables in the Informes:**
- **Table 1**: Total crimes, by category (violaciones, agresiones, etc.)
- **Table 2**: Victims (sex, age)
- **Table 3**: Perpetrators (sex)
- **Table 4**: Clearance rates

---

### Delegación del Gobierno — Intimate Partner Violence & Macroencuesta

**Contains:** Partner/ex-partner homicide registry, survey victimization data

| Type | Location |
|---|---|
| **Femicide registry** | https://violenciagenero.igualdad.gob.es/violenciaencifras/victimasmortales/fichamujeres/ → Estadística 2003–2024 |
| **Macroencuesta 2024** | https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta2024/ → Table 2.1: Lifetime prevalence |
| **Macroencuesta 2019** | https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta2015/Macroencuesta2019/ |
| **Macroencuesta 2015** | https://violenciagenero.igualdad.gob.es/violenciaencifras/estudios/colecciones/libro-22-macroencuesta/ |

---

## Verification Workflow

### For Each Row:

1. **Note the value** in the dashboard (e.g., "5,223 rape cases 2024")
2. **Click the source link 📎** (e.g., "Informe 2024 PDF")
3. **Find the table** in the PDF (usually Table 1 or appendix)
4. **Cross-check the number**:
   - ✅ **Exact match** → Confidence is justified; mark as verified
   - ⚠️ **Minor difference** (±1–2%) → Likely rounding; confidence medium-high
   - ❌ **Major difference** (>5%) → Flag as discrepancy; update SPEC.md B-section

5. **Note any caveats**:
   - Series break 2022 (LO 10/2022) → post-2022 not comparable to pre-2022
   - Pre-2012 data excludes some regions → need ×1.3–1.5 multiplier
   - Territorial exclusions → check notes column

---

## Known Issues to Watch For

### B6: Two Incompatible Violaciones Series

**The problem:** MIR Anuario lists ~5,000 violaciones/year, but MIR Informe subcategory lists ~1,200/year for the same years.

**Why?** Different definitions:
- **Anuario series (A)**: Includes Art.179 (agresión) + Art.181 (abuso) = broader definition
- **Informe series (B)**: Only Art.179 with penetration = narrower definition

**How to verify:** When you see a violaciones row:
1. Check if it's from Anuario or Informe
2. Note which series it is in the notes
3. If comparing across sources, make sure you're using the same series consistently

See `data/sources/fuentes_secundarias_analisis_espana.md` § 20 for full analysis.

---

### LO 10/2022 Series Break

**On 6 September 2022**, Spanish law merged "abuso sexual" into "agresión sexual".

**Impact:** 
- Pre-Sept 2022 figures are NOT directly comparable to post-Sept 2022 without bridging
- Our data flags this in the notes column
- Percentage changes before/after 2022 may reflect definition change, not real change

**Verification:** Check MIR Informe 2022 PDF for methodology note.

---

### Macroencuesta 2024 Methodology Change

The 2024 wave used different question wording than 2019.

**For verification:** Treat 2024 separately. Do not compare 2024 to 2019 without noting methodology change.

Check: https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta2024/ → Metodología section

---

## When to Flag a Row as Unverified

1. **Source URL is broken or unavailable** → flag as low/unverified
2. **Value doesn't match source** (>5% discrepancy without explanation) → flag as low/unverified
3. **Definition ambiguity** (e.g., which violaciones series?) → flag as medium at best
4. **Survey methodology issue** (e.g., small sample size) → flag confidence accordingly

---

## Completion Checklist

- [ ] Filter to "Sexual Violence Data" in dashboard
- [ ] Click each source link and spot-check 3–5 random years
- [ ] Verify all 2024 MIR figures match [Informe 2024](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf) Table 1
- [ ] Verify all Macroencuesta prevalence figures match published tables
- [ ] Note any discrepancies in SPEC.md §B
- [ ] Update confidence levels if needed
- [ ] Commit changes with: `git commit -m "Manual verification: sexual violence data verified against primary sources"`
