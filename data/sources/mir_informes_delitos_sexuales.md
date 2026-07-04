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

### 2021–2023 (MIR Anuario Estadístico — directly parsed via `AnuarioParser`, `data/raw/sexual_crimes_mir_anuario_2016-2023.json`)
Confirmed present in the Anuario for all 3 years (correcting the "2021 reportedly absent" note below — TABLA 3-1-5/3-1-6, "III. Libertad sexual" row, p.104 of the 2023 edition). Cross-validated field-by-field against the independently-parsed Informe series (`sexual_crimes_mir_2019-2024.json`):

| Year | Total (both series) | Agresión sexual con penetración (both series) | Match? |
|---|---|---|---|
| 2021 | 17,016 | 2,143 | exact |
| 2022 | 19,013 | 4,270 | exact |
| 2023 | 21,825 | 4,890 | exact |

For these 3 years the Anuario headline and Informe subcategory are **the same series**, not two incompatible ones — see B6 update below. The 2022 "4,890 (Geo Violencia Sexual)" figure previously logged as a same-year discrepancy (below) is actually 2023's value; likely a mismatched-year citation in that secondary source, not a real 2022 discrepancy.

One real, verified anomaly found: **2023 "Pornografía de menores"** — Informe reports 836, Anuario reports 909. Confirmed via direct PDF text dump (not a parser artifact) that the Anuario 2023 edition (p.104) literally prints `4. Pornografía de menores ... 909` for the 2023 column. Anuario's 909 exactly equals Informe's `exhibicionismo` count for 2023, and Anuario's `pornografia_menores`(909) + `otras_libertad_indemnidad_sexual`(2910) = 3,819 = the sum of Informe's other 7 categories not itemized separately by Anuario. Both publications' grand totals still agree exactly (21,825) — the two 2023 editions drew the pornografía/exhibicionismo boundary differently when collapsing categories, not a computation error. 2021 and 2022 `pornografia_menores` match exactly across both series (739 and 707 respectively), so this looks specific to the 2023 edition.

### 2016–2020 (MIR Anuario Estadístico — directly parsed, extends the table above)

`AnuarioParser`'s table-location logic was originally built against the 2021-2023 editions' table numbering (`TABLA 3-1-5`/`3-1-6`) and needed a fix to generalize backward: table numbering is **not stable** across editions (2016: `TABLA 3-1-1`; 2017-2019: `TABLA 3-1-2`; 2020: `TABLA 3-1-5`, which the 2019 edition also reuses for an unrelated table). Fixed by locating the table by **content** — presence of "HECHOS CONOCIDOS"/"HECHOS ESCLARECIDOS" column headers plus a matching "III. (Contra la) libertad sexual" total row — rather than by printed table number, with the row-match required before accepting a candidate page (guards false positives from unrelated tables sharing the same header phrase).

| Year | Anuario total | Anuario con-penetración | Cross-check |
|---|---|---|---|
| 2016 | 10,844 | 1,249 | no Informe-series year to cross-check (series starts 2019) |
| 2017 | 11,692 | 1,382 | no Informe-series year to cross-check |
| 2018 | 13,782 | 1,700 | total matches the previously-cited secondary figure (13,782) exactly; see caveat below |
| 2019 | 15,319 | 1,873 | **exact match** vs Informe 2019 (total 15,319, `agresion_sexual_con_penetracion` 1,873) |
| 2020 | 13,174 | 1,596 | **exact match** vs Informe 2020 (total 13,174, `agresion_sexual_con_penetracion` 1,596) — Informe 2020 itself newly parsed this round (2017/2018 Informe PDFs failed to parse cleanly on their older layout — 2017 returned empty, 2018 returned an internally-inconsistent total; both excluded from the Informe dataset rather than shipping wrong data, open gap) |

2019 and 2020 extend B23's exact-match finding (previously verified 2021-2023) to a 4th and 5th year — the Anuario headline and Informe subcategory are consistently the **same series** for every year 2019-2023 where both have now been directly parsed.

**Open, NOT resolved: the pre-2019 "violaciones" figure caveat below.** 2018's directly-parsed Anuario *total* (13,782) matches the old secondary-cited figure exactly, which validates that the table-location fix is finding the right table/row for these older editions. But the pre-2019 caveat's *subcategory* citations ("violaciones: 4,141 (Anuario) or 1,407 (subcategory)" for 2018; "3,716 or 1,118" for 2017) do not match the newly-parsed `agresion_sexual_con_penetracion` values (1,700 for 2018, 1,382 for 2017) under either citation. The newly-parsed values sit closer in magnitude to the old "subcategory" citation than the old "Anuario" citation, but neither matches exactly — similar in kind to the mismatched-year citation already found and resolved for 2022 (see table above). Without a working 2017/2018 Informe-side parse to cross-check against (the known open gap noted above), this cannot be conclusively resolved this round; treat the pre-2019 old secondary citations as unreliable rather than as evidence of a real ~4x divergence phenomenon.

### 2019–2025 (MIR Balance de Criminalidad — quarterly reports, directly parsed via `BalanceParser`, `data/raw/sexual_crimes_mir_balance_2019-2025.json`)

`MIR_BalanceCriminalidad_{year}_Q{1-4}.pdf` are quarterly police-crime bulletins (~490-500 pages each: one "NACIONAL" national-aggregate table plus hundreds of per-region/province tables of identical structure). The NACIONAL table's page location is **not fixed** — front page in some editions, last page in others, varying even between quarters of the same year — so `BalanceParser` scans a front+back window for a line starting `NACIONAL`. Only 2 sexual-crime subcategories are broken out (row "5.1.-Agresión sexual con penetración" and row "5.2.-Resto de delitos contra la libertad sexual", a residual bucket for everything else) — much coarser than the Anuario/Informe's 4-7 subcategories, so only the headline total (row 5) and the "con penetración" figure are meaningfully cross-checkable against the Anuario/Informe series above.

**2016-2018 could not be parsed**: these editions' NACIONAL table uses a different (pre-2019) layout that `BalanceParser`'s current row/header regexes don't match (`row 5 (total) not found` for all four 2016 quarters; `year not found in header columns []` for 2017-2018 and 2019 Q1) — `run_balance_batch` correctly detects and skips these years (emits no report) rather than shipping an empty/wrong one. Open gap, not attempted further this round; same class of older-layout problem as the 2017/2018 Informe PDFs above.

**Critical finding — these reports are cumulative year-to-date, not incremental (see B24):** each quarterly PDF's NACIONAL table is explicitly labeled "Acumulado enero a marzo/junio/septiembre/diciembre" — Q2's figure already includes Q1's crimes, Q3's includes Q1+Q2, and Q4 ("enero a diciembre") **is** the full calendar year on its own. Summing four quarters (as one might naively assume, since each quarterly bulletin looks like a discrete period) massively over-counts:

| Year | Q1 (Jan-Mar) | Q2 (Jan-Jun) | Q3 (Jan-Sep) | Q4 = annual (Jan-Dec) | Naive 4-quarter sum | Over-count |
|---|---|---|---|---|---|---|
| 2019 | n/a (Q1 unparseable, see above) | 7,258 | 11,587 | **15,338** | 34,183 (3 quarters) | n/a |
| 2020 | 3,355 | 6,139 | 10,154 | **13,240** | 32,888 | 2.5x |
| 2021 | 3,448 | 7,898 | 12,638 | **17,016** | 41,000 | 2.4x |
| 2022 | 4,191 | 9,389 | 13,455 | **17,389** | 44,424 | 2.6x |
| 2023 | 4,303 | 9,560 | 15,051 | **19,981** | 48,895 | 2.4x |
| 2024 | 4,568 | 10,010 | 16,010 | **21,159** | 51,747 | 2.4x |
| 2025 | 4,760 | 10,562 | n/a (Q3 unparseable) | **21,659** | 36,981 (3 quarters) | n/a |

The correct annual total per year is simply the Q4 report's own figure — `BalanceParser`/`run_balance_batch` parse all four quarters (to build and log this progression) but only emit the Q4 figures as that year's `MIRReport`.

Cross-validated against the Anuario/Informe series (§ above), using each year's Q4 (annual) Balance figure:

| Year | Balance total (Q4) | Anuario/Informe total | Match? | Balance con-penetración | Anuario/Informe con-penetración | Match? |
|---|---|---|---|---|---|---|
| 2019 | 15,338 | 15,319 | close (+19, +0.1%) | 1,878 | 1,873 | close (+5, +0.3%) |
| 2020 | 13,240 | 13,174 | close (+66, +0.5%) | 1,602 | 1,596 | close (+6, +0.4%) |
| 2021 | 17,016 | 17,016 | **exact** | 2,143 | 2,143 | **exact** |
| 2022 | 17,389 | 19,013 | mismatch (-1,624, -8.5%) | 2,870 | 4,270 | mismatch (-1,400, -32.8%) |
| 2023 | 19,981 | 21,825 | mismatch (-1,844, -8.5%) | 4,875 | 4,890 | close (-15, -0.3%) |
| 2024 | 21,159 | 22,846 (Informe only, no Anuario year available) | mismatch (-1,687, -7.4%) | 5,206 | 5,223 | close (-17, -0.3%) |

**2019-2021 track almost exactly (within 0.5%); 2022-2024 diverge on the total by 7-9%** (con-penetración itself stays close except 2022, which is off by a third). All Balance Q4 pages carry a "Datos pendientes de consolidar" ("data pending consolidation") disclaimer in the page header — the most plausible explanation is that Balance de Criminalidad is a **provisional** snapshot published shortly after year-end, while the Anuario/Informe series (published later, sometimes the following year) reflects **final, consolidated** figures once all reporting police bodies' data has fully arrived (the 2022 Q3 report's own text notes that Ertzaintza/Mossos d'Esquadra cybercrime data specifically "no estarán disponibles hasta el Balance anual final"). This is consistent with — and structurally analogous to — the already-documented Anuario retroactive-restatement behavior (`AnuarioParser` docstring, B9/§B6): both are cases where a later-published MIR edition revises an earlier one's counts. The consistent ~7-9% "Balance runs low" pattern for 2022-2024 (vs near-exact for 2019-2021) suggests the LO 10/2022 reform period specifically strained Balance's provisional-consolidation process, but this is not yet root-caused to a specific missing police body or category — flagged as an open item rather than silently reconciled.

The Balance's "5.2 resto" row is stored under its own key (`resto_libertad_sexual_balance`) rather than mapped onto Anuario's `otras_libertad_indemnidad_sexual`, since the two are **not** the same definition: Balance's "resto" is total-minus-con-penetración (includes sin-penetración agresión/abuso, corrupción de menores, pornografía, etc. all folded together), while Anuario's `otras_libertad_indemnidad_sexual` explicitly excludes the sin-penetración agresión-sexual subcategory (which Anuario reports separately). Treating them as equivalent would silently misrepresent both series.

**2026**: only Q1 is available so far (no Q4/annual report published yet) — correctly skipped by `run_balance_batch`, no report emitted for 2026.

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
