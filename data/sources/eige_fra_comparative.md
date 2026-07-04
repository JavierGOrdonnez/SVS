# Source: EIGE / FRA / Eurostat — EU-Comparative Gender-Based-Violence Data

**Used for:** Enabling Spain-vs-other-EU-country comparisons using standardized methodology, as a check on claims like "Spain does fine on X" against harmonised figures rather than each country's own idiosyncratic police statistics. Complements — does not replace — the Spain-only series in `macroencuesta.md` (national victimisation survey), `mir_informes_delitos_sexuales.md` (police-recorded sexual crimes), and `delegacion_gobierno_femicidio.md` (partner/ex-partner femicide registry). `homicidio_espana.md` §3 already cites EIGE for all-cause/intimate-partner homicide — this doc goes wider (IPV prevalence, sexual violence, composite indices, discrimination/hate-crime survey data) and documents *access mechanisms*, not just headline figures.

**Scope of the question:** what do the EU's two standard non-partisan comparative bodies — EIGE (Vilnius, gender-equality statistics) and FRA (Vienna, fundamental-rights victimisation surveys) — actually publish that lets Spain be benchmarked against other member states under one methodology, and how machine-readable is it.

---

## 1. EIGE — Gender Statistics Database (`dgs-p.eige.europa.eu`)

**Publisher:** European Institute for Gender Equality (EU agency, Vilnius)
**Portal:** https://eige.europa.eu/gender-statistics/dgs/browse/genvio (browse tree) — individual indicators resolve to `https://dgs-p.eige.europa.eu/data/view?code=<indicator_code>` (table viewer with a "Download" export button per indicator — code-addressable, not a single bulk file/API like Eurostat's).

### 1.1 Intimate partner / domestic violence — administrative indicators (`genvio_int_adm_ipv`)

EIGE has defined **13 indicators** on intimate partner violence (IPV) and domestic violence (DV) to standardise what police/justice administrative systems report. A second EU-wide collection round ran **2023–2024**, covering **EU-27 except Slovakia**. Example indicator codes found:

| Indicator code | Measures |
|---|---|
| `genvio_int_adm_ipv__eige_ipv_victrape` | Annual number of female/total victims of intimate-partner/domestic/any rape, as recorded by police |
| `genvio_int_adm_ipv__ipv_indic_8` | Annual number of women victims reporting rape (18+) by men (18+), as recorded by police |

Spain's EIGE country profile (https://eige.europa.eu/gender-based-violence/countries/spain) republishes exactly this administrative family for Spain, 2022: 115,980 women IPV victims (91% of all IPV victims), 139,465 women DV victims (83% of all DV victims), broken out by physical/psychological/sexual/economic sub-type, plus prosecutions/sentences/protection-order counts. These figures are **order-of-magnitude consistent with Spain's own MIR/CGPJ series already in this repo** (`mir_informes_delitos_sexuales.md`, `cgpj_violencia_genero.md`) — because they are Spain's own police/justice data, channelled through EIGE's reporting template, not an independently collected EU measure.

**Critical caveat, stated by EIGE itself:** *"The data collected across Member States should not be compared due to differences in counting rules, data collection procedures, characteristics of victims and perpetrators included, and the types of criminal offences included."* This is the same definitional-not-error framing this repo already applies to INE-vs-MIR homicide counts (`homicidio_espana.md`) — EIGE's administrative IPV/DV indicators are **not yet a like-for-like cross-country comparison tool**, only a harmonised *reporting template* that each country populates from its own legal/counting categories. Treat as Spain-only confirmation data, not a comparator, until EIGE explicitly certifies comparability.

### 1.2 Femicide — standardisation effort, still in pilot phase

**Confirmed current status (as of this pass): EIGE does NOT yet publish an operational, harmonised, per-member-state femicide count.** The work is real but pre-production:

| Milestone | Status |
|---|---|
| 2017 | EIGE begins pushing for uniform EU femicide data collection |
| 2021 | "Measuring femicide in the EU and internationally: an assessment" — comprehensive gap analysis |
| 2021-2022 | Classification system proposed: 12 types of intentional/unintentional femicide (`genvio` femicide framework) — see "Femicide: a classification system" PDF |
| 2022 | Pilot feasibility study in **7 member states** to test whether the proposed indicators could actually be populated from national data |
| 2025 | "Improving the collection of national administrative data on femicide in the EU" — latest report; still framed as capacity-building, not a published count |

Spain's own EIGE country profile lists **"1,293 women victims of intimate partner femicide, 2003–2024"** — this is not an EIGE-independent count, it is Delegación del Gobierno's own registry figure (see `delegacion_gobierno_femicidio.md`) republished by EIGE. **Do not cite this as an "EIGE femicide figure" implying independent EU verification** — it is Spain's national count, unmodified.

**Bottom line for this repo:** no cross-country femicide comparison table exists yet at EIGE. Revisit when the 2025-2026 rollout (EIGE's own 2026 roadmap names "refining methodologies for reporting on femicide" as active work) produces actual multi-country counts.

### 1.3 Gender Equality Index — violence domain (composite, context only)

| Resource | URL |
|---|---|
| Violence domain, Spain, various years | https://eige.europa.eu/gender-equality-index/2025/domain/violence/ES (JS-rendered; not machine-fetchable without a browser) |
| GEI 2025 full report | https://eige.europa.eu/sites/default/files/documents/gender-equality-index-2025-sharper-data-for-a-changing-world.pdf |
| GEI 2024 Thematic Focus ("Tackling violence against women") | https://eige.europa.eu/publications-resources/publications/gender-equality-index-2024-tackling-violence-against-women-tackling-gender-inequalities |
| Scores table (all domains, all countries) | https://dgs-p.eige.europa.eu/data/view?code=index__index_scores |

- The violence domain (added 2017, refreshed 2024 using EU-GBV survey data — see §2) has three **sub-domains: prevalence (EU-12 avg 18.2/100), severity (44.0/100), disclosure (33.5/100)**, composite EU-12 average **31.9/100**.
- **Caveat: the composite violence-domain score could only be calculated for 12 of 27 member states** in the most recent rounds (data-completeness limitation); indicator-level data is claimed for more countries but the composite score is not universal. **Whether Spain is among the scored 12 was not confirmed in this pass** (the per-country violence-domain page is JS-rendered and did not return static content to automated fetch) — flagged as an open item below.
- Spain's **overall** GEI rank (all core domains, not violence) is reported as 4th place among EU-27 in recent editions — useful context but explicitly **not a violence-specific measure**; do not conflate "Spain ranks well on the Gender Equality Index" with "Spain ranks well on gender-based violence," since violence is an *additional* domain excluded from the core Index score by EIGE's own design.

---

## 2. FRA/Eurostat/EIGE — EU Gender-Based Violence Survey (EU-GBV), 2024 edition

**This is the correct name for the "newer wave" the user asked about — it is NOT called the "Fundamental Rights Survey."** FRA does separately run a broader, general-topic "Fundamental Rights Survey" (covering discrimination, rights awareness etc. generally, not VAW-specific), but the actual successor to the 2014 "Violence against Women: an EU-wide survey" is the **EU survey on gender-based violence against women and other forms of inter-personal violence (EU-GBV)** — a **joint Eurostat + FRA + EIGE** production.

### 2.1 Coverage and methodology

| Wave | Fielded | Countries | Sample |
|---|---|---|---|
| FRA VAW survey (original) | March–Sept 2012, published 2014 | 28 EU MS | 42,000 women interviewed |
| EU-GBV survey (successor) | Sept 2020 – March 2024 (country-specific schedules) | All EU-27: 18 via Eurostat-coordinated NSI fieldwork (incl. **Spain**), Italy via its own national survey, 8 more (CZ, DE, IE, CY, LU, HU, RO, SE) via FRA/EIGE using the same methodology | 114,023 women interviewed EU-wide |

**Spain-specific fieldwork detail:** gross sample 14,370 women; **6,310 accepted interviews (43.9% response rate)**; mode = CAWI (web) first, with CATI/CAPI follow-up for non-responders. Results published **25 November 2024**, jointly by Eurostat, FRA and EIGE.

| Resource | URL |
|---|---|
| Eurostat key-results statistical report (KS-01-24-013) | https://ec.europa.eu/eurostat/web/products-statistical-reports/w/ks-01-24-013 |
| Eurostat main-findings statistical report (KS-01-24-012) | https://ec.europa.eu/eurostat/web/products-statistical-reports/w/ks-01-24-012 |
| Eurostat GBV overview/database landing page | https://ec.europa.eu/eurostat/web/gender-based-violence |
| Eurostat GBV metadata (`gbv_sims`) | https://ec.europa.eu/eurostat/cache/metadata/en/gbv_sims.htm |
| Eurostat GBV microdata access (scientific-use-file application) | https://ec.europa.eu/eurostat/web/microdata/gender-based-violence |
| EIGE key-results publication | https://eige.europa.eu/publications-resources/publications/eu-gender-based-violence-survey-key-results |
| Eurostat news release, "Every third woman..." | https://ec.europa.eu/eurostat/web/products-eurostat-news/w/ddn-20241125-3 |

### 2.2 Access mechanism — confirmed machine-readable, no parser needed

**This is directly, programmatically accessible — not PDF-only.** Confirmed working in this research pass via the Eurostat REST API:

```
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gbv_ipv_type?format=JSON&lang=en
```

Table family: `gbv_*` (e.g. `gbv_ipv_type` = intimate-partner-violence prevalence by type). Dimensions: frequency, violence-type (25 categories, e.g. "psychological, physical (incl. threats) or sexual", "sexual" only, "physical" only, etc.), unit (%), geo (31 entities incl. `EU27_2020` and all member states), time. ES (Spain) returns real, non-empty values with quality flags (`e` = estimated seen on some cells). This can be pulled with a simple HTTP GET — **no new PDF parser required**, unlike almost everything else in this repo's `data/sources/`.

**Also available:** the interactive Eurostat data browser (`ec.europa.eu/eurostat/databrowser/view/gbv_ipv_type/default/table`) for manual exploration, plus a bulk-download page.

**Microdata (respondent-level) is NOT open-download** — requires a formal scientific-use-file application to Eurostat, restricted to "recognised research entities." The public API/database only exposes aggregated indicator tables (still sufficient for country-comparison purposes).

### 2.3 Confirmed country figures (lifetime IPV — psychological, physical incl. threats, or sexual — by intimate partner)

Pulled directly from `gbv_ipv_type` via the API above:

| Country | Value | Note |
|---|---|---|
| Sweden (SE) | 48.2% | Highest of the group pulled |
| Germany (DE) | 31.9% | |
| France (FR) | 30.2% | |
| Spain (ES) | 28.6–30.0%¹ | ¹Two separate API pulls in this pass returned slightly different values (28.6% and 30.0%) for what should be the same cell — likely a query-filter artifact (different violence-type sub-code or geo aggregation selected), not a real discrepancy. **Verify exact table/filter combination before citing a single number.** |
| Italy (IT) | 25.9% | Italy uses its own national survey, not Eurostat-coordinated fieldwork — same table, different collection vehicle |

**The "Nordic paradox" caveat — directly relevant to any "Spain does fine on X" framing:** Sweden's much higher self-reported prevalence than Spain's is a well-documented pattern in the academic literature (e.g. Gracia & Merlo, *PLOS One* 2016, "Prevalence of intimate partner violence against women in Sweden and Spain: a psychometric study of the 'Nordic paradox'"), attributed to **better disclosure and less normalisation of violence in more gender-equal societies, not necessarily higher true incidence in Sweden or lower true incidence in Spain**. Any comparison built on these numbers must carry this caveat explicitly — a naive read would make Spain look "better" than Sweden on gender violence, which the literature that produced this exact dataset warns against.

### 2.4 2014 vs 2024 wave — NOT a valid time series

The original 2014 FRA survey reported Spain's lifetime partner-violence prevalence at **13%** — one of the lowest in the EU-28 at the time. The 2024 EU-GBV figure for the same concept is **~28.6-30%**. This is **not a real doubling of violence in Spain over a decade** — it reflects a substantial methodology/question-design change between the 2012-fielded FRA survey and the 2020-2024-fielded EU-GBV survey (different questionnaire, different mode mix, refined definitions). This is the exact same trap already flagged in `macroencuesta.md` for Spain's own 2019-vs-2024 wave discontinuity ("proceso estadístico de mejora... NOT directly comparable") — **do not chain 2014 and 2024 FRA/EU-GBV Spain figures into one trend line.**

### 2.5 Methodology contrast vs. Macroencuesta (Spain's national survey)

| Dimension | EU-GBV (FRA/Eurostat/EIGE, 2024) | Macroencuesta 2024 (Spain, `macroencuesta.md`) |
|---|---|---|
| Recall period | Lifetime + (separately) recent | Lifetime + last-12-months (2019 wave had a clean 12-month figure; 2024 comparability tbd) |
| Sample (Spain) | n=6,310, 43.9% response rate, CAWI-first then CATI/CAPI | n=11,894, fieldwork Sept 2024–Apr 2025 |
| Population | Women 18+ (varies by module; EU harmonised age floor) | Women 15+ (varies by module — 16+ for some) |
| Violence categories | Psychological / physical (incl. threats) / sexual, by partner and non-partner separately, plus childhood violence, stalking, workplace sexual harassment | Similar categories but Spain-specific question wording, includes "acoso sexual" (36.2% lifetime) and a 2024-new "rape by any perpetrator" module (3.1%) with no EU-GBV equivalent tested here |
| Question wording | Standardised EU instrument, translated/adapted per country | National instrument, revised between waves (2019→2024 "mejora" break already flagged) |
| Designed for | Cross-country comparison (EU-27) | Spain-only trend + dark-figure estimation |

**Implication:** Spain's Macroencuesta and the EU-GBV survey are **not simply interchangeable numbers for the same concept** even though both are victimisation surveys of Spanish women — different age floors, different recall-period defaults per published headline, different question banks. Any Spain-vs-EU comparison should use the EU-GBV figure for cross-country ranking (that's what it's designed for) and keep Macroencuesta for Spain-internal trend/dark-figure work (that's what it's designed for) — do not average or merge them.

---

## 3. EU-MIDIS — resolving the flagged gap from `discurso_odio_inmigracion_espana.md`

That doc's §2.3bis flags two open items: (a) no Spain-specific EU-MIDIS breakouts found, only EU-aggregate, and (b) a previously-circulated "FRA 86%/14%" underreporting figure that couldn't be traced to a primary source.

**Progress made in this pass — item (a) is only partially unresolved; Spain-level EU-MIDIS II data DOES exist, contrary to the prior "EU-aggregate only" framing:**

1. **A country-specific FRA PDF exists and its URL is confirmed live**: `https://fra.europa.eu/sites/default/files/fra_uploads/fra-2019-eu-midis-ii-summary-results-country-sheet-spain_en.pdf` (298KB, follows the same naming pattern as the confirmed-working Germany sheet). WebFetch could not extract readable text from it in this pass (binary/FlateDecode PDF stream not decoded by the fetch tool) — **this is a tooling limitation, not evidence the data doesn't exist.** A local `pdftotext` or the `pdf` skill should extract it directly; flagged as a concrete next step below.
2. **FRA's interactive EU-MIDIS data explorer has a Spain-specific configuration**, pre-filtered to Spain's two surveyed subgroups (North African immigrants and Roma) — reachable from https://fra.europa.eu/en/content/country-data.
3. **A Spain-focused secondary academic analysis exists and cites concrete Spain-level figures**: Bermejo & co-authors (title translates to "Discrimination and victimisation of minorities in Spain: the research potential of the EU-MIDIS project"), *Revista Española de Investigación Criminológica* (REIC), vol. 19, extra issue 2, 2021. Open-access at https://reic.criminologia.net/index.php/journal/article/view/513 (also on Dialnet: https://dialnet.unirioja.es/servlet/articulo?codigo=8331352). This paper works directly from the EU-MIDIS II **Spain subsample, N=1,563** (North African immigrants + Roma, fielded 2015-16) — i.e. Spain-level microdata is openly available and has already been used for Spain-specific research.

**Spain-specific figures recovered via secondary sources in this pass** (not yet traced to the primary country-sheet PDF itself — medium confidence, flagged for upgrade once the PDF is text-extracted):

| Metric | Spain | EU average | Source |
|---|---|---|---|
| Antigypsism/ethnic discrimination (Roma respondents, 5-yr recall) | 35% | 27% | Secondary summary of EU-MIDIS II country sheet, via gitanos.org |
| Perceived ethnic-profiling police stops | 21% | 8% | Same |
| Reporting rate for most recent discrimination incident | 12% | — | Same |

**What is still NOT resolved:** the specific **violence/harassment reporting-rate breakdown (the 88%/90%/72% figures already in `discurso_odio_inmigracion_espana.md` §2.3bis)** isolated to Spain rather than EU-aggregate. The figures recovered above are discrimination/profiling rates, not the hate-violence-reporting rates. **Getting that specific number still requires either successfully text-extracting the Spain country-sheet PDF, or pulling the REIC article's full tables (only the abstract was accessible via WebFetch in this pass — the article is methodological/proposes future analyses more than it reports exhaustive findings), or querying the FRA microdata/data-explorer directly.**

**Item (b), the "FRA 86%/14%" figure:** not investigated further in this pass (out of scope for this doc — remains flagged unverified/superseded in `discurso_odio_inmigracion_espana.md`, no new information found).

| Resource | URL |
|---|---|
| EU-MIDIS II Spain country sheet (PDF, text-extraction needed) | https://fra.europa.eu/sites/default/files/fra_uploads/fra-2019-eu-midis-ii-summary-results-country-sheet-spain_en.pdf |
| FRA country-data hub | https://fra.europa.eu/en/content/country-data |
| REIC article (Spain-specific academic analysis, open access) | https://reic.criminologia.net/index.php/journal/article/view/513 |
| Dialnet mirror | https://dialnet.unirioja.es/servlet/articulo?codigo=8331352 |

**Confidence:** medium for the three Spain-specific figures above (secondary press/NGO summary of the primary country sheet, not yet independently verified against the PDF itself); high for the *existence* of Spain-level EU-MIDIS II data (URL confirmed live, academic paper confirms Spain-subsample N=1,563 is real and analysable) — this supersedes the prior "no Spain-specific breakouts found" framing, which should be softened to "not yet extracted" in `discurso_odio_inmigracion_espana.md`.

---

## 4. Comparability mapping — EIGE/FRA vs. this repo's existing Spain series

| This repo's Spain series | EIGE/FRA analogue | Homologous? |
|---|---|---|
| MIR sexual crimes by category (`mir_informes_delitos_sexuales.md`) — police-recorded | EIGE `genvio_int_adm_ipv` administrative indicators — also police/justice-recorded | **Superficially similar, not directly comparable.** Same data type (administrative/police), but EIGE's own documentation says cross-country counting-rule differences block comparison; Spain's LO 10/2022 abuso→agresión merger (already flagged in `mir_informes_delitos_sexuales.md`) has no guaranteed EU-wide equivalent-timing counterpart |
| Delegación del Gobierno femicide registry (`delegacion_gobierno_femicidio.md`) — LO 1/2004 scope | EIGE femicide classification/harmonisation effort | **Not yet comparable — EIGE has no operational cross-country count.** EIGE's Spain figure is Delegación's own number republished, not an independent EU measure. Revisit once EIGE's 2025-2026 femicide-reporting rollout produces multi-country data |
| Macroencuesta prevalence (`macroencuesta.md`) — Spain-only victimisation survey | FRA/Eurostat/EIGE EU-GBV survey (§2) | **Closest thing to genuinely homologous in this whole doc** — both are self-report victimisation surveys of comparable design intent — but different age floors, different question banks, different fieldwork years/modes (see §2.5 table). Use EU-GBV for cross-country ranking, Macroencuesta for Spain-internal trend; do not merge |
| — (no existing repo series) | EIGE Gender Equality Index, violence domain | New indicator, not previously tracked in this repo. Composite score, not a raw prevalence/incidence count — useful as one summary number per country but sub-indicator provenance should be checked before citing (mixes EU-GBV survey data with administrative data per country, per §1.3) |
| `discurso_odio_inmigracion_espana.md` hate-crime/discrimination series | EU-MIDIS II (§3) | Discrimination/hate-crime-experience survey vs. Spain's own police-recorded hate-crime series (`InformeDelitosOdio`) — same "survey vs. police-report" dark-figure relationship already used elsewhere in this repo (`macroencuesta.md` vs MIR sexual crimes) |

---

## 5. Access mechanism summary

| Source | Mechanism | Parser needed? |
|---|---|---|
| Eurostat EU-GBV survey aggregated indicators (`gbv_*` tables) | **REST API / data browser, JSON, confirmed working** | **No** — direct HTTP pull, e.g. `.../data/gbv_ipv_type?format=JSON` |
| Eurostat EU-GBV survey microdata | Formal application, "recognised research entity" scientific-use-file process | N/A — access-gated, not a parsing problem |
| EIGE Gender Statistics Database (`genvio_*` indicators incl. IPV/DV administrative data) | Code-addressable table viewer (`dgs-p.eige.europa.eu/data/view?code=...`) with a Download/export button per indicator | Likely no PDF parser — but format of the "Download" export (CSV vs Excel) not confirmed in this pass; check on first real pull |
| EIGE Gender Equality Index scores/domains | Same `dgs-p` viewer for the scores table; per-country/per-domain pages are JS-rendered (not fetchable headlessly) | No parser for the scores table; the narrative per-country pages would need a real browser render, not WebFetch |
| EIGE femicide harmonisation | **Not yet operational** — no multi-country dataset exists to pull | N/A until EIGE publishes one |
| FRA EU-MIDIS II country sheets | PDF, one per country, confirmed URLs live | **Yes** — needs the `pdf` skill or `pdftotext`; WebFetch alone could not decode this PDF's text in this pass |
| FRA EU-MIDIS II interactive data explorer | Web app (JS-rendered), Spain-preconfigured view exists | No parser, but not headlessly fetchable either — needs manual/browser pull |
| REIC academic article on Spain EU-MIDIS II | Open-access HTML/PDF via journal site or Dialnet | Possibly — abstract-only was fetchable in this pass; full tables would need direct PDF handling |

---

## 6. What to pull next (concrete scoping for a future parsing/extraction task)

1. **Highest value, lowest effort:** pull `gbv_ipv_type` and sibling `gbv_*` tables (non-partner violence, sexual harassment at work, stalking, childhood violence — check `gbv_sims.htm` metadata page for the full table list) from the Eurostat API for **ES, FR, DE, IT, SE** plus `EU27_2020` — this is a same-day task, no parser needed, just HTTP GET + JSON handling. Gives a genuinely comparable Spain-vs-EU-4 prevalence table for the repo's first real cross-country VAW comparison.
2. **EU-MIDIS II Spain country sheet**: fetch the PDF at the confirmed URL above through the `pdf` skill (not plain WebFetch, which failed to decode it) — this should directly resolve the open Spain-isolated violence/harassment-reporting-rate gap flagged in `discurso_odio_inmigracion_espana.md` §2.3bis, upgrading it from "unresolved" to a sourced figure.
3. **EIGE `genvio_int_adm_ipv` indicator family**: pull the full 13-indicator set for Spain (already partially summarised via the country-profile page in this pass) plus 2-3 comparator countries, to see concretely how large the "counting rules differ, don't compare" gap actually is in practice — useful even as a negative/caveat-establishing result.
4. **EIGE Gender Equality Index violence-domain scores**, all countries, via the `dgs-p.eige.europa.eu/data/view?code=index__index_scores`-style endpoint (confirm the exact code for the violence sub-domain specifically) — resolves the open question in §1.3 of whether Spain is among the 12 countries with a calculated composite score.
5. **REIC article full tables** (Bermejo et al. 2021) — request/locate the full PDF (only the abstract was reachable in this pass) for any additional Spain-specific EU-MIDIS II figures beyond the three discrimination/profiling numbers already recovered.
6. Lower priority: EIGE's femicide-harmonisation 2025/2026 outputs — check back later in 2026 per EIGE's own stated roadmap ("refining methodologies for reporting on femicide" is listed as active 2026 work) for whether an actual multi-country count has been published yet.

---

## Open follow-ups

- Confirmed live URLs and one working figure retrieval (Eurostat API) in this pass; two sources (EIGE per-country domain pages, FRA EU-MIDIS II PDF) need either the `pdf` skill or a real browser render rather than plain WebFetch — both are access/tooling gaps, not evidence the data doesn't exist.
- The 28.6% vs 30.0% discrepancy for Spain's EU-GBV lifetime-IPV figure (§2.3) needs to be resolved by pinning the exact table/dimension filter before this number is cited as a headline figure anywhere else in the repo.
- Whether Spain is among the 12 EU member states with a calculated Gender Equality Index violence-domain composite score is unconfirmed (§1.3).
- EIGE's administrative IPV/DV indicators explicitly should not be used for cross-country ranking per EIGE's own stated caveat — if a future task wants a genuinely comparable administrative (not survey) figure, that gap is currently unfilled by any EU body.
