# Source: Homicide Statistics — Spain (All-Cause, by Sex)

Multiple sources required for full picture: INE ECM (cause-of-death), MIR Balance (police-registered), EIGE (harmonised EU), feminicidio.net (NGO, broader definition).

---

## 1. INE — Estadística de Defunciones según la Causa de Muerte (ECM)

**ICD-10 codes:** X85–Y09 (agresiones — intentional homicide) + Y87.1 (sequelae)
**Unit:** Deaths occurring in calendar year

| Resource | URL |
|---|---|
| Press release 2023 (provisional) | https://www.ine.es/dyngs/Prensa/pEDCM2023.htm |
| ODS Indicator 16.1.1 — homicide rate by sex | https://www.ine.es/dyngs/ODS/es/indicador.htm?id=5254 |
| Main operation page | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176780&menu=resultados&idp=1254735573175 |
| Defunciones por causas (lista reducida) t=7947 | https://www.ine.es/jaxiT3/Tabla.htm?t=7947 |
| Homicide rate by sex and period (ICV) | https://www.ine.es/jaxi/Tabla.htm?path=%2Ft00%2FICV%2FGraficos%2Fdim6%2Fl0%2F&file=611G2.px&L=0 |

### Confirmed figures

| Year | Total | Female | Male | Rate/100k | Confidence |
|---|---|---|---|---|---|
| 2001 | — | — | — | 1.40 | medium (historical max) |
| 2013 | — | — | — | 0.60 | medium (series min) |
| 2021 | — | — | — | 0.62 | medium |
| 2023 | ~300 | ~96 | ~204 | 0.68 | high (press report) / medium (sex breakdown) |

**Caveats:**
- INE ECM counts deaths by cause in calendar year. A homicide occurring in December may be recorded in the following year if death follows later.
- Lower than MIR police count (2023: 300 vs 348) because: INE requires confirmed medical cause of death; MIR counts police-registered incidents including those with unknown/pending outcome.

---

## 2. MIR — Balance de Criminalidad (police-registered homicides)

**Series:** Homicidios dolosos y asesinatos consumados — police-registered, all regions (including Mossos, Ertzaintza since ~2014)
**Unit:** Police-reported completed homicides in calendar period (cumulative YTD per quarterly report)

| Report | URL |
|---|---|
| Q4 2025 (full year 2025) | https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2025/Balance-de-Criminalidad_Cuarto_Trimestre_2025.pdf |
| Q4 2024 (full year 2024) | https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/BALANCE-CRIMINALIDAD-CUARTO-TRIMESTRE-2024.pdf |
| Q4 2023 (full year 2023) | https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2023/Balance-de-Criminalidad-Cuarto-Trimestre-2023.pdf |
| Anuario 2023 (provisional) | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/dam/jcr:78fcbb84-3a16-4de7-abed-1364f4ecd770/Anuario_estadistico_2023_126150729_Prov.pdf |

### Confirmed police counts (full year)

| Year | Total consumados | Notes | Confidence |
|---|---|---|---|
| 2023 | ~348 | From Q4 2023 balance, cited in 2025 comparative analysis | medium |
| 2024 | ~349 | Back-calculated from 2025 = 376, +7.7% | low (verify directly) |
| 2025 | 376 | +7.7% vs 2024; highest since 2012 | high |

**Note:** The MIR balance does NOT routinely publish victim sex breakdown in the headline tables. Detailed sex breakdown requires the annual Anuario Estadístico or the MIR Informe sobre el Homicidio.

---

## 3. EIGE — European Institute for Gender Equality

**Source:** Harmonised EU statistics on gender-based violence, using national administrative data reported to EIGE.

| Resource | URL |
|---|---|
| Spain country profile | https://eige.europa.eu/gender-based-violence/countries/spain |
| Gender Equality Index 2023 — Violence domain | https://eige.europa.eu/gender-equality-index/2023/domain/violence/ES |

### Key 2022 figures (high confidence — EIGE harmonised)

| Category | Total | Female | Female % |
|---|---|---|---|
| All-cause homicide | 325 | 121 | 37% |
| By intimate partner | 58 | 54 | 93% |
| By domestic perpetrator | 98 | 80 | 82% |

**Note on "intimate partner" discrepancy:** Delegación del Gobierno counts 49 female victims by intimate partner in 2022 (LO 1/2004 scope). EIGE counts 54 — EIGE uses a broader definition that may include some cases Delegación classifies differently (e.g. non-cohabiting ex-partners, or cases pending final judicial determination at the time of Delegación count).

---

## 4. MIR — Primer Informe Nacional sobre el Homicidio en España (2010–2012)

**Coverage:** Cleared homicide cases 2010–2012 (more than half of all homicides in those years)
**URL:** https://www.interior.gob.es/opencms/pdf/prensa/balances-e-informes/2018/INFORME-HOMICIDIOS-2010_2012.pdf

### Key findings (medium confidence — cleared cases only, not population-representative)

| Metric | Value |
|---|---|
| Male perpetrators | 89% |
| Female perpetrators | 11% |
| Male victims (source narrative) | 61% |
| Female victims (source narrative) | 39% |
| Victim-perp matrix: Male → Male | 62% |
| Victim-perp matrix: Male → Female | 28% |
| Victim-perp matrix: Female → Male | 7% |
| Victim-perp matrix: Female → Female | 3% |

**Note on internal discrepancy:** The narrative says "61% of victims are male" but the matrix (62+7=69% male, 28+3=31% female) gives different figures. Likely due to rounding in the matrix, or the matrix covers a sub-sample. Use "61% male / 39% female" as the best available figure for victim sex from this period.

---

## 5. Feminicidio.net — NGO broader-definition count

**Definition:** All women killed by men, regardless of relationship, including cases where perpetration is presumed. Broader than official Delegación count.
**URL series:** https://feminicidio.net/

### 2023 (medium confidence)

| Metric | Value |
|---|---|
| Total women killed by men | 103 |
| Of which feminicides (91.3%) | 94 |
| By intimate partner | 56 |
| By family member (outside partner) | 12 |
| By social/sexual context | 10 |

**Cross-check with INE ECM 2023:** INE says 96 total female homicide victims (all perpetrators). Feminicidio.net says 103 by male perpetrators. Difference (7): some cases may involve female perpetrators, disputed cases, or different year assignment.

---

## Source Compatibility Matrix

| Series | Scope | Unit | Sex breakdown? | Perpetrator sex? |
|---|---|---|---|---|
| INE ECM (ICD X85-Y09) | All regions, all victims | Deaths by cause | Yes (table t=7947) | No |
| MIR Balance | Police-registered, all regions | Incidents | Not in headline | Not in headline |
| MIR Anuario / Informe | Police-registered, cleared cases | Cases | Yes (Anuario tables) | Yes (Informe) |
| EIGE | EU harmonised | EIGE classification | Yes | Partial |
| feminicidio.net | Female victims only | NGO count | Female only | Yes (male only) |
| Delegación del Gobierno | Partner/ex-partner, LO 1/2004 | Registry | Female only | Male only |

## TODO

- Extract INE table t=7947 for annual homicide deaths by sex 2000–2023
- Obtain MIR Anuario 2022/2023/2024 tables with victim sex breakdown
- Reconcile EIGE 2022 intimate partner figure (54) vs Delegación (49)
- Verify 2024 MIR balance total (est. ~349) against primary PDF
