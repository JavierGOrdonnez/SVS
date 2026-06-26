# Source: LGTBI-phobic hate crimes in Spain — incidence + victim/aggressor sex & nationality, 2013–2025

**Used for:** SPEC §F (Hate-speech & Migration correlation, T37–T40) — the LGTBI-phobia ("orientación sexual e identidad de género", OSIG) slice of Spain's official hate-crime series, parallel to `discurso_odio_inmigracion_espana.md`'s racism/xenophobia slice. Primary target was the **sex and nationality of both victims and aggressors**, year by year 2015–2025 — that crosstab is the hard-to-find piece and is reported with explicit confidence flags below per V14/V18 (relative claims must be paired with the underlying breakdown, not asserted from aggregate figures).

**Scope of the question:** annual count of OSIG hate crimes ("hechos conocidos") in Spain 2013–2025; for each year, the sex distribution of victims and of investigated/arrested aggressors *specific to the OSIG category*; and separately, the nationality (Spanish/foreign) distribution of victims and aggressors *specific to the OSIG category* — flagged sharply below because, at the national level, this last breakdown **does not exist as a published category-specific crosstab** (only as an all-motivations aggregate, plus one regional exception).

---

## 1. Methodological foundation — read this before using any figure below

Ministerio del Interior publishes an annual **"Informe sobre la evolución de los delitos de odio en España"** since the 2013 data year. It tracks hate crimes ("hechos conocidos") across ~11 "ámbitos" (motivation categories): racismo/xenofobia, antisemitismo, aporofobia, creencias o prácticas religiosas, discapacidad, ideología, discriminación por sexo/género, discriminación generacional, discriminación por enfermedad, antigitanismo, and **"orientación sexual e identidad de género."**

**Finding 1 — the category has never been split.** In every report examined (2018 through 2025) sexual orientation and gender identity are tracked as **one single combined ámbito**, never two separate line items. Earlier academic literature covering 2011–2015 calls the same combined category "orientación o identidad sexual" — different wording, same single bucket. No methodological break exists in this dimension across the whole 2013–2025 series (contrast with the racism/xenophobia "hechos esclarecidos → hechos conocidos" metric break documented in `discurso_odio_inmigracion_espana.md` §2.1).

**Finding 2 — sex crosstabs exist category-specific; nationality crosstabs do not (nationally).** The national report's sections 3 ("Perfil de la víctima: ámbito, sexo y edad") and 4 ("Perfil del autor: ámbito, sexo y edad") publish a **"distribución porcentual... por ámbito según sexo"** table — i.e. sex *is* broken out per ámbito, including OSIG specifically. After reading the full 2021, 2022 and 2023 national reports, **no equivalent ámbito × nationality crosstab exists** — the closest the report gets is an age-group × nationality crosstab (all ámbitos combined) that only *mentions* OSIG qualitatively (e.g. "los ámbitos de mayor incidencia en hombres jóvenes son racismo/xenofobia y orientación sexual e identidad de género") without isolating a nationality percentage for it. **This means every "nationality of LGTBI-phobia victims/aggressors" figure circulating from the national series is an all-motivations aggregate, not OSIG-specific, unless explicitly marked otherwise below.**

**The one exception:** Andalucía's regional government report reproduces the underlying microdata (from MIR's "Portal Estadístico de Criminalidad") at finer grain than the national publication, including a true OSIG-specific nationality crosstab for Andalucía-only data, 2020 (§4).

---

## 2. Year-by-year headline counts (OSIG hechos conocidos, national)

| Year | Hechos conocidos | Source | Confidence |
|---|---|---|---|
| 2013 | **452 reported, unconfirmed/likely unreliable** — see §6 anomaly | FELGTBI "Informe Delitos de Odio" PDF | low — conflicts with the otherwise-consistent series; could not be corroborated against any other source |
| 2014 | not found | — | — (confirmed gap) |
| 2015 | 169 | FELGTB 2018 report (`felgtb_violencias.txt`), p.2 | medium |
| 2016 | 230 | FELGTB 2018 report, p.2 | medium |
| 2017 | 271 (back-calculated from "−4.4% vs. 2017" stated for 2018's 259) | Observatorio Madrileño contra la LGTBIfobia, *Informe sobre incidentes de Odio por LGTBfobia en la Comunidad de Madrid 2019* | medium |
| 2018 | 259 | FELGTBI "Estado del odio" 2024 report, Tabla 1; cross-confirmed by Observatorio Madrileño 2019 report quoting MIR's 2018 national report | high |
| 2019 | 278 | FELGTBI "Estado del odio" 2024 report, Tabla 1 | medium |
| 2020 | 277 | FELGTBI "Estado del odio" 2024 report, Tabla 1 | medium |
| 2021 | 466 | FELGTBI "Estado del odio" 2024 report, Tabla 1; confirmed directly in the official MIR 2021 national report | high |
| 2022 | 459 | FELGTBI "Estado del odio" 2024 report, Tabla 1; confirmed directly in the official MIR 2022 national report | high |
| 2023 | 522 | Official MIR 2023 national report, direct table read ("Orientación sexual e identidad de género: 522... ascenso de 13,73% con respecto a las cifras del [2022]"); cross-confirmed by La Moncloa's 2023 hate-crime press release | high |
| 2024 | 528 | La Moncloa press release, 2025-07-18, on the 2024 national report | medium-high (headline count corroborated by press note; underlying PDF table not independently re-confirmed in this pass — see §6) |
| 2025 | 571 (+23.6% vs. 2024, per the all-motivations headline cited in SPEC §V18) | interior.gob.es press coverage of the 2025 report (exact PDF/press-note URL not pinned down in this pass — flagged below) | low-medium — figure found only via secondary press coverage, not the primary table; treat as provisional until the primary 2025 PDF is pulled |

---

## 3. Victim sex — OSIG-specific (the reliable part of the series)

| Year | Male victims | Female victims | Other/undisclosed | % male | Source |
|---|---|---|---|---|---|
| 2018 | 213 | 99 | — | 68% | Observatorio Madrileño 2019 report, quoting MIR 2018: "213 víctimas y 99 mujeres... 68% de hombres a un 32% para mujeres" |
| 2021 | 398 | 132 | 0 | 75.09% | Official MIR 2021 national report, "Victimizaciones de delitos de odio registradas según sexo" table |
| 2022 | 377 | 148 | 3 | 71.40% (71.48% per FELGTBI's own recomputation) | Official MIR 2022 national report; cross-confirmed by FELGTBI "Estado del odio" 2024: "377 son hombres y 148 son mujeres... un 71,48% son hombres y un 28,19% mujeres" |
| 2023 | 419 | 134 | 2 | 75.50% | Official MIR 2023 national report, direct table + percentage chart (~76%/24%) |
| 2024 | not isolated — see §6 anomaly | not isolated | — | — | press-reported 59.91% male is an **all-motivations aggregate**, not OSIG-specific (see caveat) |

**Pattern:** across the three years with a confirmed OSIG-specific breakdown (2021–2023), victims run consistently **~68–76% male, ~24–32% female** — notably more male-skewed than the racism/xenophobia category's victim profile (59.9% male in 2024, per `discurso_odio_inmigracion_espana.md` §2.1).

## 4. Aggressor/perpetrator sex — OSIG-specific

| Year | Male aggressors | Female aggressors | % male | Source |
|---|---|---|---|---|
| 2018 | 94 | 11 | 92% | Observatorio Madrileño 2019 report, quoting MIR 2018: "94 hombres y 11 mujeres... 92% de hombres y 8% de mujeres" |
| 2021 | 176 | 33 | 84.21% | Official MIR 2021 national report, "Detenciones / investigados por delito de odio según sexo" table |
| 2022 | 189 | 34 | 84.75% | Official MIR 2022 national report |
| 2023 | 224 | 45 | 83.27% | Official MIR 2023 national report, direct table + percentage chart (83%/17%) |
| 2024 | not isolated — see §6 anomaly | not isolated | — | press-reported 81.9% male is an **all-motivations aggregate** (matches the figure already in `discurso_odio_inmigracion_espana.md` §2.1), not OSIG-specific |

**Pattern:** OSIG aggressors run **~83–92% male** across every year with category-specific data — markedly more male-skewed than the victim side, and broadly consistent with the all-motivations aggressor profile (81.9% male in 2024) but running a few points higher.

## 5. Nationality — what is actually available

**National level:** no OSIG-specific nationality crosstab is published for victims or aggressors in any year reviewed (2021–2023 read in full). All-motivations aggregates exist (e.g. 2024: 60.1% Spanish / 39.9% foreign victims, 75.6% Spanish aggressors, per `discurso_odio_inmigracion_espana.md` §2.1; 2021/2023 aggregate Spanish-victim shares of 65.53%/62.15%, aggregate Spanish-aggressor shares of 75.64%/78.73%, per the MIR 2021/2023 reports) — but these mix all eleven ámbitos together and **cannot be attributed to the OSIG category specifically**.

**Regional exception — Andalucía 2020 (the one true category-specific crosstab found):**

| | Spanish | Foreign | % Spanish |
|---|---|---|---|
| OSIG victims | 33 | 3 | 91.7% (of 36) |
| OSIG aggressors | 14 | 2 | 87.5% (of 16) |

Source: Junta de Andalucía, *II Informe Estadístico para la elaboración de Políticas Públicas Antidiscriminatorias en el ámbito LGTBI*, Tablas 12/15/16/19, citing "Fuente: Ministerio del Interior. Portal Estadístico de Criminalidad. 2020." Same report's sex crosstab for the same year/region: victims 31M/5F (86.1%/13.9%), aggressors 16M/0F (100%).

**Caveat:** this is Andalucía-only, one year (2020), and drawn from the *Portal Estadístico de Criminalidad* microdata layer that regional governments can query at finer grain than the national report publishes — it demonstrates the data exists somewhere in MIR's system, not that it is publicly available nationally or for other years.

---

## 6. Discrepancies / anomalies flagged

- **2013 "452" figure:** FELGTBI's own PDF states "siendo en 2013, primer año de análisis con 452 al 2021 con 466" — roughly double the otherwise-stable ~170–280 range seen 2015–2020, and uncorroborated by any other source reviewed. Possible explanations not resolved in this pass: a typo, confusion with a different metric (e.g. cumulative victims rather than hechos), or a genuine first-year methodological inflation before the series stabilized. **Treat as unconfirmed; do not chain into the 2015–2025 series without flagging.**
- **2024 sex splits likely conflated with all-motivations aggregate:** press-reported "59.91% male victims / 81.9% male aggressors" for 2024 diverge sharply from the 71–76%/83–85% category-specific range seen in 2021–2023 — strongly suggesting the press coverage (and by extension this doc's §2 2024 row) is citing the all-motivations aggregate, not an OSIG-isolated figure. The full 2024 PDF could not be independently re-pulled in this pass (interior.gob.es returned 403; no working mirror found) to confirm the true OSIG-specific 2024 sex split. **Flagged as an open gap, not resolved as fact.**
- **A previously-circulated claim of more foreign than Spanish OSIG victims** (encountered in one secondary academic source, not re-verified this session) conflicts with the consistent ~60–92% Spanish-majority pattern found across every other source in this doc (national aggregate and Andalucía-specific alike). Flagged as needing verification before use, not included as a data point above.

---

## 7. Secondary / civil-society sources consulted

| Source | What it adds | Caveat |
|---|---|---|
| FELGTB / FELGTBI (Federación Estatal LGTBI+) — annual "Estado del odio" reports | Reproduces and contextualizes MIR's OSIG hechos-conocidos series back to 2013 in one table (Tabla 1); independently recomputes MIR's own percentage splits | Advocacy organization re-publishing official MIR figures, not an independent count — useful as a secondary cross-check, not a primary source in its own right |
| Observatorio Madrileño contra la Homofobia, Transfobia y Bifobia (Comunidad de Madrid, run via Arcópoli) — annual reports | Earliest source found quoting MIR's category-specific sex breakdown directly (2018 data, published 2019) | Regional advocacy report; for Madrid-region incidents plus its own quoting of the national MIR table |
| Junta de Andalucía — *II Informe Estadístico... ámbito LGTBI* | The only category-specific **nationality** crosstab located (§4) | Andalucía-only, 2020 only |
| OCH (Observatori Contra l'Homofòbia, Catalonia) — annual reports | Case-based incident tracking with victim trans-identity detail (e.g. "8 homes trans, 29 dones trans" in 2021) | Narrative/case-based, **zero quantitative aggressor sex or nationality data** found |
| Mossos d'Esquadra (Catalonia) | Aggregate case-count trend (761 cases 2023, +18.7%; 43% of 2021 hate-crime cases were OSIG-motivated) | No perpetrator sex/nationality breakdown isolated to OSIG found |
| ILGA-Europe Rainbow Europe / Annual Review | Legal/policy ranking (Spain #1 in 2026) + qualitative survey narrative ("assaults against LGBTI people up 15% since 2024," physical-assault share "tripling from 7% to 22%" in a 2026 perception survey) | **Not a quantitative hechos-conocidos or aggressor-demographic dataset** — different methodology (perception survey, EU-wide), do not merge with the MIR police-recorded series |
| López Ortega, A.I., "Análisis y evolución de los delitos de odio en España (2011–2015)," *Antropología Experimental* 17, Texto 2 (2017) | Earliest sex-specific figure found: "100% de varones" registered in the "orientación o identidad sexual" ámbito, 2011–2015 aggregate | Pre-dates the 2015–2025 focus window but corroborates the strong male-skew pattern from the very start of the series |

| Resource | URL |
|---|---|
| MIR 2021 national report | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/dam/jcr:583fbc03-0f4a-42eb-a2cd-93be7421f4c5/INFORME%20EVOLUCION%20DELITOS%20DE%20ODIO%202021.pdf |
| MIR 2022 national report (third-party mirror; interior.gob.es original blocked) | https://migrantesenigualdad.es/wp-content/uploads/2024/05/Informe_Evolucion_delitos_odio_2022.pdf |
| MIR 2023 national report | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/dam/jcr:b8edc382-ad73-47b6-af8c-7dc81d9a4557/INFORME%20EVOLUCION%20DELITOS%20DE%20ODIO%202023.pdf |
| La Moncloa note, 2024 report (incl. headline OSIG=528 context) | https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/interior/paginas/2025/180725-informe-delitos-odio.aspx |
| FELGTBI, "Estado del odio: Estado LGTBI+ 2024" | https://felgtbi.org/wp-content/uploads/2024/08/Informe-DDOO_24.pdf |
| Observatorio Madrileño contra la LGTBIfobia, Informe 2019 (covers 2018 data) | https://contraelodio.org/wp/wp-content/uploads/2020/10/Informe-Comunidad-de-Madrid-2019-v2.pdf |
| Junta de Andalucía, *II Informe Estadístico... ámbito LGTBI* | https://www.juntadeandalucia.es/sites/default/files/2023-03/v2-INTERACTIVO%20INFORME%20LGTBI%202022.pdf |
| López Ortega (2017), UJA academic article | https://revistaselectronicas.ujaen.es/index.php/rae/article/download/3197/2830/11745 |

**Confidence:** high for 2021–2023 headline counts and category-specific sex splits (cross-confirmed directly against the primary MIR PDF tables); medium for 2015–2020 headline counts (FELGTBI/regional secondary republication of MIR figures, not the primary PDF re-read directly in this pass); medium-high for 2024 headline count (press-corroborated) but **2024 sex split is flagged as likely an all-motivations aggregate, not OSIG-specific** — open gap; low-medium for 2025 (secondary press coverage only, primary PDF not pulled); high for the Andalucía 2020 nationality crosstab (official regional government report citing the MIR statistical portal directly) but explicitly scoped to one region/one year; low for the 2013 "452" figure (uncorroborated, likely erroneous — see §6); n/a for ILGA-Europe (different methodology, not comparable to the police-recorded series).

---

## 8. Confirmed gaps (searched, not found — for future follow-up)

- Exact 2014 OSIG hechos-conocidos figure — not located in any source.
- National-level OSIG-specific sex crosstabs for 2024 and 2025 — primary PDFs return 403 on interior.gob.es; no working mirror found on estadisticasdecriminalidad.ses.mir.es (mirrors only through 2023) or oficinanacional-delitosdeodio.ses.mir.es (503 errors during this pass).
- Any year's national-level OSIG × nationality crosstab for victims or aggressors, beyond the single Andalucía 2020 regional exception — confirmed absent from the published national report structure in 2021, 2022 and 2023 (the three years read in full).
- COGAM-specific standalone statistical reports with independent aggressor data — COGAM appears to contribute to FELGTB's national observatory network and the Arcópoli-run Madrid Observatorio rather than publish a separate dataset of its own.
- A precise primary-source URL for the 2025 headline figure (571, +23.6%) — found only via secondary press coverage in this pass.
