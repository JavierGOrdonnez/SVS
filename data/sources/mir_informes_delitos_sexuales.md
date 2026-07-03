# Source: Ministerio del Interior — Informes sobre Delitos contra la Libertad Sexual

**Publisher:** Ministerio del Interior / Secretaría de Estado de Seguridad / ONVIOS (since 2024)  
**Series name:** Informe sobre Delitos contra la Libertad Sexual en España  
**Coverage:** Annual; reported crimes, victims, perpetrators  
**Available from:** 2019 (dedicated annual report series); earlier data in Anuarios Estadísticos

## Access — Annual Reports

| Year | Direct PDF URL |
|---|---|
| 2024 | https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf |
| 2023 | https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2023/INFORME-DELITOS-CONTRA-LA-LIBERTAD-SEXUAL-2023.pdf |
| 2022 | https://www.interior.gob.es/opencms/pdf/prensa/balances-e-informes/2022/INFORME-DELITOS-CONTRA-LA-LIBERTAD-SEXUAL-2022.pdf |
| 2022 (alt) | https://www.interior.gob.es/opencms/pdf/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones-descargables/publicaciones-periodicas/informe-sobre-delitos-contra-la-libertad-e-indemnidad-sexual-en-Espana/Informe_delitos_contra_libertad_sexual_2022_126210034.pdf |
| Index page (all years) | https://www.interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/informe-sobre-delitos-contra-la-libertad-e-indemnidad-sexual-en-espana/ |
| ONVIOS publications | https://onvios.ses.mir.es/publico/onvios/publicaciones.html |

## Access — Historical Anuarios (2000–2018)

| Resource | URL |
|---|---|
| Anuarios index | https://www.interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/anuario-estadistico-del-ministerio-del-interior/ |
| Portal Estadístico Criminalidad | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/ |
| Portal publications list | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/publicaciones.html |

## Key figures verified from primary sources

### 2024 (MIR Informe published Dec 2025)
- Total crimes: **22,846** (+4.68% vs 2023; +66% vs 6 years prior)
- Violaciones (agresión con penetración): **22.86%** = ~5,223
- Agresiones sexuales sin penetración: **59.85%** = ~13,673
- Total victims: 22,778 (19,518 female = **85.69%**)
- Victims under 18: **41.2%** (~9,384)
- Detained/investigated: 14,375 (**93.13% male**)
- Clearance rate: **83.3%** (highest in recent years)

### 2023 (MIR Informe published Jul 2024)
- Total crimes: **21,825** (+14.8% vs 2022)
- Violaciones: ~20% = ~4,365 (exact % pending primary PDF access)
- Total victims: 21,580 (18,464 female = **84.6%**; 3,092 male; 24 unknown)
- Victims under 18: **42%**

### 2021–2023 (MIR Anuario Estadístico — directly parsed via `AnuarioParser`, `data/raw/sexual_crimes_mir_anuario_2021-2023.json`)
Confirmed present in the Anuario for all 3 years (correcting the "2021 reportedly absent" note below — TABLA 3-1-5/3-1-6, "III. Libertad sexual" row, p.104 of the 2023 edition). Cross-validated field-by-field against the independently-parsed Informe series (`sexual_crimes_mir_2019-2024.json`):

| Year | Total (both series) | Agresión sexual con penetración (both series) | Match? |
|---|---|---|---|
| 2021 | 17,016 | 2,143 | exact |
| 2022 | 19,013 | 4,270 | exact |
| 2023 | 21,825 | 4,890 | exact |

For these 3 years the Anuario headline and Informe subcategory are **the same series**, not two incompatible ones — see B6 update below. The 2022 "4,890 (Geo Violencia Sexual)" figure previously logged as a same-year discrepancy (below) is actually 2023's value; likely a mismatched-year citation in that secondary source, not a real 2022 discrepancy.

One real, verified anomaly found: **2023 "Pornografía de menores"** — Informe reports 836, Anuario reports 909. Confirmed via direct PDF text dump (not a parser artifact) that the Anuario 2023 edition (p.104) literally prints `4. Pornografía de menores ... 909` for the 2023 column. Anuario's 909 exactly equals Informe's `exhibicionismo` count for 2023, and Anuario's `pornografia_menores`(909) + `otras_libertad_indemnidad_sexual`(2910) = 3,819 = the sum of Informe's other 7 categories not itemized separately by Anuario. Both publications' grand totals still agree exactly (21,825) — the two 2023 editions drew the pornografía/exhibicionismo boundary differently when collapsing categories, not a computation error. 2021 and 2022 `pornografia_menores` match exactly across both series (739 and 707 respectively), so this looks specific to the 2023 edition.

### 2022 (MIR Anuario)
- Total crimes: 19,013 (directly parsed, see table above — supersedes the earlier ~19,059 derived estimate)
- Violaciones: 4,270 — confirmed matching both Anuario and Informe (see table above; the earlier "4,890 discrepancy" note was a mismatched-year citation, see above)
- Agresiones sin penetración: 11,426
- Note: LO 10/2022 enacted 6 September 2022 — categories merged from that date

### Pre-2022 historical (Anuarios MIR)
- 2019: violaciones 5,453 per Anuario; BUT also cited as 1,520 in the 2019 Informe's subcategory breakdown (agresión con penetración under prior definition). **Series break: two incompatible counts — see B6 in SPEC.md.** NOTE: this pre-2019 divergence has NOT been re-examined with a direct parse (unlike 2021-2023 above, which — once directly parsed from primary PDFs — showed NO divergence); treat the ~4x claim as applying to pre-2019 years only until 2017-2019 Anuario PDFs are parsed directly.
- 2018: total delitos sexuales 13,782; violaciones 4,141 (per Anuario series) or 1,407 (subcategory)
- 2017: violaciones 3,716 (Anuario) or 1,118 (subcategory)
- 2000–2011: counts exclude Cataluña, País Vasco, Navarra (~25–30% of population) — multiply by ~1.3–1.5 to estimate national total

## Critical caveats

1. **LO 10/2022 series break**: "abuso sexual" (no force) merged into "agresión sexual" from Sept 2022. Pre-2022 and post-2022 totals are **not comparable** without bridging table.
2. **Two violaciones series (B6)** — **pre-2019 only**: the Anuario headline series (thousands) and the Informe subcategory series (hundreds/low thousands) give irreconcilable values for the same year, for 2017-2019 (only secondary/web-sourced figures checked so far). For 2021-2023, direct parsing of both primary-source PDFs shows the two series agree **exactly** on total and on the Art.179-equivalent subcategory (see table above) — the divergence does not reproduce in the post-2019 era where both series are directly parseable. Root cause of the older divergence still unresolved; see also SPEC.md §B6/B23.
3. **Territorial exclusion pre-2012**: 2000–2011 MIR data covers only Policía Nacional + Guardia Civil territory (excludes Mossos, Ertzaintza, Policía Foral Navarra).
4. **2015 gap**: Reform of Código Penal (supresión de faltas) created a methodological break.
5. **2023 "Pornografía de menores" anomaly**: Anuario 2023 edition reports 909, Informe 2023 reports 836 for the same category/year — a genuine cross-publication data anomaly, confirmed via direct PDF text (not a parser bug). See table above for the reconciling arithmetic.
