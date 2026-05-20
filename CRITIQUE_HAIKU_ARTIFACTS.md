# Critical Assessment — Haiku Model Artifacts (May 2025 conversation)

## Timeline note
Both the Haiku conversation and today are **May 2026**. Publications dated "Sept 2025" are
8 months old — the Haiku model had access to them. Figures from INE Condenados 2024 and
Fiscalía Memoria 2024 are therefore *unverified* but not necessarily fabricated from the model's
timeline perspective. They must still be checked against the actual publications (and the
arithmetic error in the INE subcategories remains a red flag regardless).

---

## TL;DR verdict

The corpus is large, self-referential, and presents itself as rigorously verified ("VERIFICADO ✓✓").
In reality it contains fabricated numbers, circular self-citation, internal contradictions, invalid
comparisons, and arithmetic errors. The 2022–2024 aggregate crime totals are broadly plausible.
Everything built around them — historical estimates, dark-figure multipliers, denuncia rates,
sub-category breakdowns — is suspect and should be treated as unverified until checked against
primary publications.

---

## 1. What looks plausible

| Claim | Why plausible |
|---|---|
| 2022 violaciones 4,270 / 2023 4,875 / 2024 5,206 | Align with public MIR portal and press coverage |
| 2022 agresiones sin penetración 11,426 / 2024 15,953 | Order of magnitude consistent with pre/post-LO10/2022 |
| Fiscalía +92% jump 2022→2023 (9,603→18,474) | Well-documented effect of LO 10/2022 reclassification |
| Macroencuesta 2019: 13.7% lifetime sexual violence outside partner | Consistent with known publication |
| Macroencuesta 2019: 9.2% by partner, 57.3% any machista violence | Consistent |
| Population base 20.4M women 16+, sample n=9,568 | Consistent with INE Padrón |
| 42.6% of sexual crime victims are minors (2023) | Plausible per Ministry reports |
| Territorial exclusion pre-2012 (Cat, PV, Nav) | Documented, well-known limitation |
| Ley 10/2022 break in series | Factually correct |

---

## 2. Confirmed wrong values (verified against primary sources, May 2026)

| Metric | Haiku value | Verified value | Source | Error |
|---|---|---|---|---|
| 2024 femicide (partner/ex) | 58 | **47** | Delegación del Gobierno ficha Feb 2025 | −11 (−19%) |
| 2024 total sexual crimes | 21,159 | **22,846** | MIR Informe 2024 (Dec 2025) | −1,687 (−7.4%) |
| 2024 agresiones sin penetración | 15,953 | **~13,673** (59.85%) | MIR Informe 2024 | −2,280 (−14.3%) |
| 2024 violaciones | 5,206 | **~5,223** (22.86%) | MIR Informe 2024 | −17 (−0.3%) — very close |
| 2023 total sexual crimes | 19,981 | **21,825** | MIR Informe 2023 (Jul 2024) | −1,844 (−8.4%) |
| 2023 violaciones | 4,875 | **~4,365** (~20%) | MIR Informe 2023 | −510 (if 20% is exact) |

**INE Condenados 2024 arithmetic note was MY ERROR** in the audit: the 90 "violaciones" is a subcategory of the 1,389 "agresiones sexuales" (not additive). The subcategories sum correctly: 1,151+1,097+1,389+1,593 = **5,230 ✓**. Haiku's INE figures appear accurate.

**51% foreign femicide victims in 2024** — confirmed. Rate ratio foreign/Spanish = 8.32/1.68 = 4.95×, consistent with Haiku's "4.9×" claim.

---

## 2b. Confirmed fabrications

### 2a. Arithmetic error in INE Condenados 2024 subcategories
The model presents subcategories for adult convictions 2024:
`1,151 + 1,097 + 1,389 + 90 + 1,593 = 5,320 ≠ stated total 5,230`.
The claimed total is off by 90. Whether this is a transcription error from the real publication
or a confabulation, the numbers as presented are internally inconsistent. These were published
Sept 2025 (8 months before the Haiku conversation) so the model could have accessed them,
but the arithmetic error undermines confidence. Verify against actual INE publication.

### 2b. The "62× ratio" (methodologically invalid)
Divides 2019 annual denuncias (~5,453) by 2019 Macroencuesta *lifetime* prevalence (1,322,052 women
who experienced sexual violence from age 15 across their entire lives). Incompatible denominators
(incident/year vs. person-ever over ~50 years). The "62×" is not a dark-figure multiplier — it is
an artifact of mixing units. Presented throughout as a key finding.

### 2c. Historical estimates 2000–2014 dressed as data
Round-number estimates (2,300 / 2,400 / 2,500 / 3,000 / 3,500) with source "MIR LIMITADO /
estimado académico" are explicitly noted as estimates in footnotes, then the overall file claims
"CALIDAD: Excelente (múltiples validaciones cruzadas)." The actual Anuarios PDFs were never
downloaded.

### 2d. CIS Estudio 3182 (2015) linked to La Manada
La Manada assaults occurred July 2016; a 2015 survey could not reference the case.
Chronologically impossible.

### 2e. COVID "+30-50% real violence"
Speculative range from academic commentary, presented as a measured fact four times identically
across separate documents.

### 2f. "51% feminicidios 2024 were migrant women / 4.9× risk"
Directionally plausible (foreign women are overrepresented in IPV homicides), but the specific
4.9× multiplier and 51% figure appear with no document, page, or table reference across multiple
files. Likely confabulated.

### 2g. Annual estimated hidden cases (~1M+/year)
The corpus at one point implies >1M annual sexual violence cases. Spain has ~47M inhabitants.
No European country shows rates near this. Not derived from stated methodology.

---

## 3. Internal contradictions

| Metric | Value A | Value B | Value C |
|---|---|---|---|
| Female % of 2023 victims | 84.6% | 86% | ~89% |
| Spanish aggressors 2023 | 62.7% | 68% (claimed 2024) | — |
| Rape denuncia rate | 6% | 8% | 15.9% / 16% |
| Total 2023 delitos sexuales | 19,981 | 21,825 | 21,580 |
| 2022 violaciones | 4,270 | 4,890 | — |
| Minor conviction trend 2023 | −21.4% vs 2022 | +45.8% proceedings | — |
| Clearance rate (esclarecimiento) sexual crimes | 77.9%→81.1% (one table) | 75.8%→77.5% (another table) | — |

---

## 4. Systemic methodology failures

1. **Self-certification**: "VERIFICADO ✓✓" applied to values the model generated without document
   access, not against primary sources.
2. **Circular sourcing**: "Verified in FASE 2" refers to other files from the same model session.
3. **Citation laundering**: Infobae (news site) cited alongside Ministry reports with equal ✓ weight.
4. **Denominator confusion**: Lifetime prevalence, annual denuncias, and annual incidence estimates
   mixed without explicit unit labelling in summary tables.
5. **The "CERO INFERENCIAS" claim**: The model repeatedly asserts it made zero inferences while
   openly labelling half its historical series as "estimado."

---

## 5. Critical unresolved issue: two incompatible "violaciones" series

FASE_3 lists: 2017=3,716 / 2018=4,141 / 2019=5,453 (labeled "violaciones, Anuario MIR")

FASE_2_TAREA_2.1 lists (from Interior Informe 2019, subcategory "agresión con penetración"):
2017=1,118 / 2018=1,407 / 2019=1,520

These differ by a factor of ~2.9–3.6 for identical years. The model describes this as
"divergen ligeramente." It is not slight — it implies different legal definitions or scope.
This must be resolved before any incidence-rate computation. Likely explanation: the larger
series includes "abuso sexual con penetración" (now merged post-2022), while the smaller series
is narrowly "agresión sexual con penetración" (requiring force, pre-2022 definition).

---

## 6. What to verify first (priority order)

1. MIR Anuarios 2022–2024 + Informe Delitos Libertad Sexual 2023/2024 — resolve the two
   violaciones series and get exact victim demographics.
2. Fiscalía Memoria 2024 (now published, Sept 2025) — verify the 20,711 / +12.11% claim.
3. INE Condenados 2024 (now published, Sept 2025) — verify / replace fabricated subcategories.
4. Delegación del Gobierno feminicidio annual report 2024 — verify or reject 51% migrant claim.
5. Macroencuesta 2019 full PDF — verify exact table references for prevalence figures.
6. Ballesteros & Blanco (2021) in EMPIRIA — check whether the specific data attributed to it
   actually appears in that paper.

---

## 7. What is definitely salvageable

The conceptual framework the Haiku model built is largely sound:
- Correct identification of the four major methodological breaks (2003, 2012, 2015, 2022)
- Correct warning about pre-2012 territorial exclusion
- Correct source list (MIR, CGPJ, Fiscalía, Macroencuesta, INE Condenados)
- Correct observation that denuncias ≪ actual incidence
- Correct note that the 2022 law makes pre/post series incomparable

The *values* need primary-source verification. The *structure* is a reasonable starting point.
