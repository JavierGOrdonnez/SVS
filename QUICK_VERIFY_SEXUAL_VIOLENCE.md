# Quick Verification — Sexual Violence Data

## One-Click Verification Workflow

### Step 1: Open Dashboard
```
docs/index.html → Open in browser
```

### Step 2: Navigate to Sexual Violence Charts
These charts have embedded source links:
1. **Total Sexual Crimes Reported — MIR 2018–2024**
2. **Rape (Agresión con Penetración) — MIR 2017–2024**
3. **Sexual Crime Victims 2024 — By Sex**
4. **Sexual Crime Victims 2024 — By Age Group**
5. **Sexual Crime Perpetrators 2024 — By Sex**

### Step 3: Click Any Source Link
Example from "Total Sexual Crimes Reported" chart:

```
Official: "Delitos contra la libertad sexual. ⚠ 2022 definitional break: 
[LO 10/2022] merged "abuso sexual" into "agresión sexual"..."
                          ↑ click here
```

This opens:
- 📎 **MIR Informe 2024** (2024 sexual crime figures)
- 📋 **LO 10/2022 law text** (defines the series break)

---

## Spot-Check Values

### 2024 Total Sexual Crimes

**Dashboard shows:** Should display ~22,846 total crimes  
**To verify:**
1. Click "[MIR Informe 2024](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf)"
2. Go to **Table 1** ("Delitos contra la libertad sexual 2024")
3. Check row "Total" = **22,846** ✓

### 2024 Rape Count

**Dashboard shows:** Should display ~5,223  
**To verify:**
1. Click same MIR Informe 2024 link
2. Look for "Violaciones (agresión con penetración)" row
3. Check value ≈ **5,223** (or 22.86% of 22,846)

**⚠️ B6 Issue:** If you see ~1,200, that's the Informe subcategory (Art.179 only). We use the Anuario headline (~5,223) which includes both Art.179 + Art.181.

### 2024 Victim Breakdown

**Dashboard shows:**
- Female victims: 85.69% (19,518 of 22,778)
- Under 18: 41.2%

**To verify:**
1. Click "[MIR Informe 2024](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf)"
2. Go to **Tables 2–3** (victim demographics)
3. Check:
   - Female/total = 19,518/22,778 ✓
   - Under 18 row ✓

---

## B6 Known Issue: Two Violaciones Series

### What's the problem?

Two different MIR sources give incompatible rape counts for the same years:

| Source | 2024 | 2019 | 2017 |
|---|---|---|---|
| **Anuario headline** | 5,223 | 5,453 | 3,716 |
| **Informe subcategory** | ~1,200 | 1,520 | 1,118 |

### Why?

- **Anuario (A)** = Art.179 (agresión) + Art.181 (abuso) = **broad definition**
- **Informe (B)** = Art.179 only (con penetración) = **narrow definition**

### Which do we use?

**We use Anuario (the larger series).** It's more consistent pre-2022 but requires noting the definition includes both agresión and abuso.

### How to verify the discrepancy:

1. Click "[MIR Anuario](https://www.interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/anuario-estadistico-del-ministerio-del-interior/)" link
2. Search for "violaciones" or "delitos sexuales" chapter
3. Find "Violaciones" row → ~5,223 for 2024 ✓

Then:

4. Click "[Informe subcategory](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf)" link
5. Look for Art.179 subcategory → ~1,200 for 2024
6. Note the difference and why ← This is B6

---

## LO 10/2022 Series Break

**Date:** September 6, 2022  
**What changed:** "Abuso sexual" (no force) merged into "Agresión sexual" (force/coercion)

### Impact:
- **Pre-Sept 2022:** Abuso and agresión were separate categories
- **Post-Sept 2022:** All non-consensual sexual acts = "agresión sexual"

### Verification:

1. Click "[LO 10/2022 (Solo sí es sí)](https://www.boe.es/diario_oficial/pdf/BOE-A-2022-14630.pdf)" link → see the law itself
2. Or check MIR Informe 2022 methodology section → explains the definition change
3. Note: 2022 values are affected by the change mid-year

---

## Macroencuesta Surveys

### Lifetime Prevalence of Sexual Violence

**Chart:** Macroencuesta de Violencia contra la Mujer — Lifetime Prevalence by Wave

**Links:**
- 🔗 [2015 wave](https://violenciagenero.igualdad.gob.es/violenciaencifras/estudios/colecciones/libro-22-macroencuesta/)
- 🔗 [2019 wave](https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta2015/Macroencuesta2019/home.htm)
- 🔗 [2024 wave](https://violenciagenero.igualdad.gob.es/violenciaEncifras/macroencuesta2024/)

### What to verify:

1. Click **2024 link**
2. Go to **Table 2.1** (lifetime prevalence)
3. Check "Violencia sexual" row → should show ~7% lifetime prevalence
4. Check **methodological note** → explains 2024 methodology change
5. Note: 2024 NOT directly comparable to 2019 without methodology caveat

---

## Summary Verification Checklist

- [ ] All 2024 MIR numbers match [MIR Informe 2024](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf)
- [ ] 2024 victim percentages sum correctly (female 85.69%, male 13.77%, unknown <1%)
- [ ] 2023 figures cross-checked against [MIR Informe 2023](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2023/INFORME-DELITOS-CONTRA-LA-LIBERTAD-SEXUAL-2023.pdf)
- [ ] B6 note documented (Anuario vs Informe discrepancy explained)
- [ ] 2022 series break documented (LO 10/2022 link provided)
- [ ] Macroencuesta 2024 methodology caveat noted (not comparable to 2019)
- [ ] Confidence levels assigned based on verification:
  - 🟢 **High** = exact match to official source
  - 🟡 **Medium** = minor discrepancy or secondary source
  - 🟠 **Low** = significant gap or ambiguity
  - 🔴 **Unverified** = unable to verify against source

Once all checks pass → ready to merge branches 2 & 3
