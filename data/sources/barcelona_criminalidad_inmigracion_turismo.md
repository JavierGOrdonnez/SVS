# Source catalogue: General & sexual crime in Barcelona (city + province) — immigration vs. tourism framing

**Used for:** Scoping doc for a possible new SPEC thread — a Barcelona-specific companion to the
national work in `mir_informes_delitos_sexuales.md` (sexual crime) and `migracion_espana.md`
(migration denominators), extended to **general crime** (theft, robbery, pickpocketing — currently
**not covered anywhere in this repo**, which is sexual-violence/femicide/hate-crime scoped only, per
`SPEC.md` §G). Not yet a primary data table — no parser exists for any source below; this is the
"which sources exist and what do they actually measure" scoping step that should precede one, in
the same spirit as `fuentes_secundarias_analisis_espana.md` / `discurso_odio_inmigracion_espana.md`.

**The question this is meant to serve:** the popular debate is "immigration inflow has driven a
crime surge" vs. "it's just ordinary tourist-city petty theft" — and per the repo's own C8
(associative ≠ causal) and C11 (nationality/ethnicity breakdowns sparse in official data), neither
side of that claim is answerable from a single source. It needs **at least three separate series**,
which is why this catalogue is organized that way:

1. **Crime counts**, broken out by *type* (violent/sexual crime vs. property/petty theft — these
   have very different perpetrator/victim profiles) and by *geography* (city vs. province — Barcelona
   province is much more than Barcelona city).
2. **Population/immigration denominators** at the same geography, to compute rates, not raw counts.
3. **Tourism-flow denominators** (visitor-days, not just resident population) — a huge share of
   Barcelona's reported theft/pickpocketing has tourists as victims, not residents, so a per-resident
   rate alone will overstate the "risk to a Barcelona resident" framing and a per-tourist-day rate is
   needed for the "opportunistic tourist-theft" side of the claim.

None of the sources below report perpetrator nationality at city/province level publicly (same gap
flagged nationally in `mir_informes_delitos_sexuales.md` T26 and SPEC.md C11) — this is the single
biggest open gap for the "immigration → crime" causal question specifically, as opposed to the
"is crime up, and is it violent or petty" descriptive question, which is well covered.

---

## 1. What's already usable from this repo (national-level, needs disaggregating or caveating)

| Existing doc | Usable how | Caveat for Barcelona-specific use |
|---|---|---|
| `mir_informes_delitos_sexuales.md` | National sexual-crime trend as a baseline to compare Barcelona/Catalonia against | National only; **2000–2011 MIR national figures exclude Mossos d'Esquadra territory** (i.e. exclude Catalonia) entirely — pre-2012 national series is not a valid Catalonia baseline. Post-2012 the national series should include Mossos, but Catalonia is not broken out in the already-downloaded `MIR_Anuario`/`MIR_Informe` PDFs |
| `data/sources/*/MIR_BalanceCriminalidad_*.pdf` (already downloaded, 2016 Q1–2026 Q1) | Each quarterly PDF is ~490–500 pages: **one NACIONAL table plus hundreds of per-region/province tables of identical structure** (per `mir_informes_delitos_sexuales.md` §"2019–2025 Balance"). A Barcelona-province table almost certainly already exists inside these PDFs, unparsed | No `BalanceParser` support for the per-province tables yet — only the NACIONAL table is currently extracted (`src/parsers/mir_parser.py`). Extending the parser to pull the Barcelona rows would reuse files already in the repo, no new download needed |
| `migracion_espana.md` | INE EMCR table **24322** (migration flow by **province**, year, sex, age, nationality) and table **24312** (by CCAA) are already documented and would resolve directly to "Barcelona" as a province filter | Only flow, not stock; Padrón/ECP stock tables in this doc (36825, 68535, 31304) are national-only in the doc as written — the province/municipality equivalents exist at INE but aren't yet listed (see §3 below for the Idescat alternative, which is easier to query for Catalan geography) |
| `discurso_odio_inmigracion_espana.md` | Directly relevant context: documents the "crime-framed migration discourse → hate speech → real aggression" mechanism nationally, incl. Catalan case study (Ca n'Anglada 1999) | No Barcelona-2024-26-specific incident cataloguing yet; would need updating if this thread proceeds |
| `qa_recidivism_foreign_offenders.md` | Legal-framework background (Art. 89 CP expulsion, libertad vigilada) applies uniformly across Spain, incl. Catalonia | Not geography-specific, background only |
| `SPEC.md` C11 | Standing caveat: nationality/ethnicity breakdowns are sparse in Spanish official crime data generally | Applies with full force at the sub-national level too — expect this gap to be *worse*, not better, at city/province granularity |

**Bottom line:** the repo has strong sexual-violence and migration-denominator infrastructure that
generalizes to Barcelona with moderate effort (province-level INE tables already identified; MIR
Balance PDFs already contain unparsed provincial tables), but **zero general-crime (theft/robbery)
data of any kind** — that has to come from the sources in §2 below, all new to this repo.

---

## 2. Crime-count sources specific to Barcelona / Catalonia

### 2.1 Ministerio del Interior — Portal Estadístico de Criminalidad (SEC), interactive query tool

**Distinct from** the Balance PDFs already in the repo — this is a separate, queryable online tool
(not a downloadable PDF series) covering **national, autonomous-community, provincial, and
municipal** levels for 2017–2025, across the full crime-type taxonomy (not just sexual crimes) —
i.e. it directly answers "conventional crime" (theft, robbery, burglary) vs. "crimes against sexual
freedom" as separate filterable categories for Barcelona city/province specifically.

| Resource | URL |
|---|---|
| Portal home | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/ |
| Query/search tool | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/busqueda.html |
| Quarterly balance landing page | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/balances |

**Confidence:** high for existence/access mechanism (portal confirmed live, geographic granularity
confirmed down to municipal level); figures not yet pulled. **Caveat:** "conventional crime" (delitos
convencionales) figures in this system are police-recorded counts covering Policía Nacional, Guardia
Civil, **and** Mossos d'Esquadra/Ertzaintza jurisdictions since a mid-2010s data-sharing agreement —
confirm coverage completeness for Barcelona specifically before trusting any municipal total as
exhaustive (Guàrdia Urbana, Barcelona's *local* police, may or may not feed into this system the same
way — cross-check against §2.4).

### 2.2 Mossos d'Esquadra (Generalitat de Catalunya) — regional police statistics

Catalonia's own police force publishes its own statistics independent of the MIR national system —
this is the actual primary source for anything policed by Mossos rather than Policía
Nacional/Guardia Civil, which for Barcelona province is most territory outside Barcelona city itself.

| Resource | URL |
|---|---|
| Estadística policial (Mossos) | https://mossos.gencat.cat/ca/els_mossos_desquadra/indicadors_i_qualitat/estadistica/ |
| Web de dades obertes dels Mossos d'Esquadra (open-data catalogue entry) | https://datos.gob.es/en/catalogo/a09002970-web-de-datos-abiertos-de-los-mossos-desquadra |
| Institut de Seguretat Pública de Catalunya (ISPC) — dades estadístiques sobre seguretat | https://ispc.gencat.cat/ca/1_linstitut/centre_coneixement_seguretat/fons_documental/dades-estadistiques-sobre-seguretat/ |

**Confidence:** medium — portal existence confirmed, and a recent press figure was surfaced
(Catalonia-wide 2025: 495,742 total criminal infractions, −2.9% YoY; conventional crime 422,563
(−2.7%); cybercrime 73,179 (−3.8%); homicides/murders 58 vs 69 (−16%); vehicle theft 8,632 (+1%);
drug trafficking +11%) but this was from press coverage of the Mossos annual balance, not yet
traced to the primary table, and is Catalonia-wide, not Barcelona-province-specific — needs
re-extraction from the primary release with province-level breakdown before citing.
**Caveat:** Mossos organizes territory into "regions policials," which do not map 1:1 onto
INE's "provincia de Barcelona" boundary — reconciling the two geographies (or picking one
consistently) is a needed methodological step before joining Mossos data to INE population/migration
denominators.

### 2.3 Idescat — Estadística de seguretat ciutadana

Catalonia's official statistics institute; publishes citizen-security stats designed to be
comparable across Catalan geography (comarca, including Barcelonès and the wider metropolitan
comarques that make up most of Barcelona province).

| Resource | URL |
|---|---|
| Idescat — Estadística de seguretat ciutadana, Catalunya | https://www.idescat.cat/pub/?id=sci |
| Barcelona Dades (Ajuntament) — "Fets penals coneguts per la Policia de Catalunya" | https://portaldades.ajuntament.barcelona.cat/estad%C3%ADstiques/co6rdrzcdj |

**Confidence:** medium — a recent headline figure surfaced (Catalonia known-crime rate H1 2026:
32.68 facts/1,000 inhabitants, −9.9% YoY) but not yet pinned to a specific table/breakdown; not
yet confirmed whether Idescat's series is a repackaging of Mossos data (§2.2) or an independently
compiled series — needs checking before treating them as two independent cross-checks rather than
one series counted twice.

### 2.4 Ajuntament de Barcelona — Guàrdia Urbana crime balance + Open Data BCN

Barcelona city's own local police force (Guàrdia Urbana, distinct from Mossos) publishes an annual
"Balanç dels fets delictius" — this is the most city-specific (not province-wide) source, and the
natural home for the "tourist-theft" side of the question since Guàrdia Urbana is the force most
engaged with reporting in tourist-dense districts (Ciutat Vella, Eixample, Sants-Montjuïc).

| Resource | URL |
|---|---|
| Balanç dels fets delictius a la ciutat 2023 (example annual release) | https://ajuntament.barcelona.cat/guardiaurbana/ca/noticia/balanc-dels-fets-delictius-a-la-ciutat-el-2023_1371693 |
| English version | https://ajuntament.barcelona.cat/guardiaurbana/en/noticia/balanc-dels-fets-delictius-a-la-ciutat-el-2023_1371745 |
| Open Data BCN — city open-data portal (search here for the machine-readable dataset) | https://opendata-ajuntament.barcelona.cat/ |
| Barcelona Dades — "Nombre de fets delictius coneguts" (city analytics portal, likely the easiest queryable entry point) | https://portaldades.ajuntament.barcelona.cat/estad%C3%ADstiques/y75sdijf4u |
| Pla Local de Seguretat de Barcelona 2024–2027 (policy document with baseline stats + district breakdown) | https://ajuntament.barcelona.cat/seguretatiprevencio/sites/default/files/2024-07/Pla%20Local%20de%20Seguretat_2024_2027.pdf |

**Confidence:** medium — annual press releases with headline city totals confirmed to exist and be
regularly published (2023 release found: incidents −7.3% vs. pre-pandemic 2019 but +8.6% vs. 2022);
district-level and category-level (theft vs. violent crime vs. sexual crime) breakdowns not yet
confirmed extractable — check Open Data BCN's dataset directly rather than the press-release PDFs,
which likely only report city-wide headline totals.
**Caveat:** Guàrdia Urbana ≠ Mossos ≠ Policía Nacional — three separate forces can each record an
incident depending on who a victim reports to, and Barcelona city sits inside Mossos jurisdiction
too (Mossos took over general public-order policing from Policía Nacional across Catalonia in the
2000s). Cross-tabulating without double-counting risk requires understanding which force has primary
recording responsibility for which crime type — likely Mossos for anything meeting the *penal code*
threshold (i.e. anything that would show up in §2.1/§2.2) with Guàrdia Urbana focused on municipal
ordinances plus first-response/local presence, but this needs confirming, not assuming.

### 2.5 Enquesta de Victimització de Barcelona (EVB) / metropolitan EVAMB — Institut Metròpoli

This is the closest Barcelona-level analogue to `macroencuesta.md` (national victimisation survey) —
a **survey-based**, not police-report-based, measure, which is exactly the tool needed to
distinguish "reported theft is up" from "actual theft is up" (dark-figure correction), and it also
separately measures *perceived* insecurity, which is the right instrument for the "moral panic vs.
real trend" side of the debate.

| Resource | URL |
|---|---|
| Institut Metròpoli — Convivència i seguretat urbana (survey series landing page) | https://www.institutmetropoli.cat/ca/enquestes/convivencia-i-seguretat-urbana/ |
| "Percepció d'inseguretat a Barcelona" — July 2025 full report (PDF) | https://www.institutmetropoli.cat/wp-content/uploads/2025/10/Percepci%C3%B3-dinseguretat-BCN_informe-complet-1.pdf |
| Ajuntament — factors of insecurity by neighborhood (2023 report) | https://ajuntament.barcelona.cat/seguretatiprevencio/sites/default/files/2023-08/informe_sobre_els_factors_de_la_inseguretat_als_barris_de_barcelona.pdf |
| Generalitat — Enquesta de Seguretat Pública de Catalunya (regional-scale equivalent) | https://govern.cat/gov/notes-premsa/117490/enquesta-seguretat-publica-marca-tendencia-estabilitzacio-victimitzacio-percepcio-seguretat-millora-valoracio-dels-serveis-policials |

**Confidence:** medium — series existence and recent headline finding confirmed (July 2025: Barcelona
perceived-security score 5.5/10, below the Catalan average; insecurity has polled as Barcelonans'
top-ranked civic concern since late 2018, per municipal barometer). Methodology/questionnaire not yet
reviewed — needs the same "is this comparable wave to wave" check `macroencuesta.md` already applies
nationally (2019 vs. 2024 wording change) before trending it.
**Caveat — same class as macroencuesta.md's core caveat:** perceived insecurity and actual
victimisation rate are related but distinct outcomes; conflating "Barcelona residents feel less safe"
with "Barcelona crime rate has risen" would repeat exactly the survey-vs-reported-crime conflation
this repo already guards against nationally.

### 2.6 Institut Català de les Dones — gender-based violence / femicide, Catalonia-specific registry

Parallel Catalan-government registry to the national `delegacion_gobierno_femicidio.md` source, with
a **broader scope**: since 2018 the Catalan count includes *all* homicides of women by men (not just
intimate-partner/ex-partner, per LO 1/2004's narrower national definition) — directly relevant since
that's exactly the kind of definitional mismatch the repo already flags nationally as something never
to merge across without labeling.

| Resource | URL |
|---|---|
| Dades estadístiques — Observatori de la Igualtat de Gènere | https://dones.gencat.cat/ca/ambits/Observatori-de-Igualtat-de-Genere/violencies-masclistes/Dades-estadistiques-00033 |
| Dossiers estadístics (annual, incl. Dossier 2024) | https://dones.gencat.cat/ca/ambits/Observatori-de-la-Igualtat-de-Genere/dossiers-estadistics/ |
| Dossier estadístic — 10 anys de dades sobre violències masclistes (PDF) | https://dones.gencat.cat/web/.content/03_ambits/Observatori/03_dossiers_estadistics/Dossier_estadistic_10_anys_VM_4.pdf |

**Confidence:** medium — headline figures surfaced (156 femicides in Catalonia since 2012 per the
broader post-2018 definition; 2024: 17,452 women attended at SIAD services) but not yet pinned to a
specific table, and **not yet province/Barcelona-specific** — this is Catalonia-wide; whether it
breaks out Barcelona province/city needs checking in the primary Dossier PDF.
**Caveat:** definitional break is explicit and dated (2018 scope widening) — do **not** treat this as
directly comparable to `delegacion_gobierno_femicidio.md`'s national LO 1/2004-scoped series without
the same kind of bridging table this repo already requires for other definitional breaks (C3).

---

## 3. Population / immigration denominators at Barcelona geography

Needed to convert any of §2's raw counts into rates, and to test the "immigration inflow" side of
the claim against an actual denominator rather than raw counts (which will rise with population
regardless of composition).

| Resource | Geography | URL |
|---|---|---|
| INE EMCR table 24322 — migration flow by **province**, year, sex, age, nationality (already in `migracion_espana.md`) | Province (Barcelona = filter value) | https://www.ine.es/jaxiT3/Tabla.htm?t=24322&L=0 |
| INE EMCR table 24312 — migration flow by **CCAA** (already in `migracion_espana.md`) | Autonomous community (Catalonia) | https://www.ine.es/jaxiT3/Tabla.htm?t=24312&L=0 |
| Idescat — Població estrangera a 1 de gener, per municipis | Municipality (Barcelona city + every municipality in the province) | https://www.idescat.cat/poblacioestrangera/?b=6 |
| Idescat — Població estrangera, per districtes (Barcelona city breakdown) | City district | https://www.idescat.cat/poblacioestrangera/?b=10&geo=mun%3A080193 |
| Idescat — Població estrangera, per països (Barcelona city, by country of origin) | Municipality × country | https://www.idescat.cat/poblacioestrangera/?geo=mun%3A080193&nac=a&b=12 |
| Idescat — Padró municipal d'habitants, Barcelona (population by nationality/continent + place of birth) | Municipality | https://www.idescat.cat/pub/?id=pmh&n=682&geo=mun:080193 |
| Barcelona Dades — Taxa (%) de població estrangera | City (with district drill-down) | https://portaldades.ajuntament.barcelona.cat/ca/estad%C3%ADstiques/srdhxemdph |

**Confidence:** high for existence/access (Idescat's municipal/district-level foreign-population tool
is live and directly queryable; one headline figure confirmed: Barcelonès comarca foreign-population
share 24.9%, foreign-*born* share 34.1% — among the three highest comarques in Catalonia). Figures
not yet pulled into this repo's format.
**Caveat:** "Barcelonès" (the comarca containing Barcelona city + 4 adjoining municipalities) ≠
"Barcelona province" (7 comarques, ~5.5M people) ≠ "Barcelona city" (~1.7M) — always state which of
the three geographies a given figure uses; press coverage frequently blurs this distinction, and it
matters enormously for the immigration-share claim specifically (Barcelonès's 24.9% foreign share is
not representative of the province average).

---

## 4. Tourism-flow denominators (the "just petty tourist-crime" side of the claim)

A per-resident crime rate cannot evaluate the "it's tourism-driven petty theft" claim — that claim is
about crime **per visitor**, or about the composition of victims (tourists vs. residents), not about
the resident population at all. These sources are the tourism-side equivalent of §3's migration
denominators.

| Resource | URL |
|---|---|
| INE FRONTUR — Estadística de Movimientos Turísticos en Frontera (foreign visitor arrivals, monthly + annual) | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176996&menu=ultiDatos&idp=1254735576863 |
| INE table 2073 — Viajeros y pernoctaciones por provincias | https://www.ine.es/jaxiT3/Tabla.htm?t=2073&L=0 |
| INE table 2074 — Viajeros y pernoctaciones por CCAA y provincias | https://www.ine.es/jaxiT3/Tabla.htm?t=2074 |
| INE table 2078 — Viajeros y pernoctaciones por puntos turísticos (city-level, incl. Barcelona) | https://www.ine.es/jaxiT3/Tabla.htm?t=2078&L=0 |
| Idescat — Indicadors de conjuntura: visitants estrangers, turistes i excursionistes | https://www.idescat.cat/indicadors/?id=conj&n=10305&lang=es |

**Confidence:** high for existence/access (all are standard, long-running INE/Idescat operations with
direct province- and city-level tables already identified). Not yet pulled.
**Caveat:** FRONTUR/EGATUR count *foreign* visitors only — Barcelona also receives large domestic
(other-Spain) tourist flows not captured here; INE's hotel-occupancy survey (Encuesta de Ocupación
Hotelera, not yet listed above — would need a separate table lookup) would be needed to capture
total (domestic + foreign) overnight-stay volume as the fullest "visitor-days" denominator. Also note
overnight-stays undercounts excursionists/day-trippers (e.g. cruise passengers, a well-known
Barcelona-specific tourist segment relevant to petty theft around the port/cruise terminal) — FRONTUR
does track excursionistas separately from turistas; don't silently drop that category.

---

## 5. Open items before any of this becomes a real SPEC task

- **No source above yet confirmed to publish suspect/perpetrator nationality at city/province
  level.** This is the crux of the "immigration drove the increase" causal claim specifically (as
  opposed to the purely descriptive "is crime up" question, which §2 covers well) and is the single
  biggest gap — worth an explicit search/confirmation pass (Mossos annual "Memòria" documents,
  Fiscalia de Catalunya memorias, or CGPJ Catalonia-level judicial stats might have it even if police
  press releases don't) before promising this analysis can answer that half of the question.
- Geography reconciliation needed across sources: Mossos "regions policials" vs. INE
  "provincia de Barcelona" vs. Idescat "comarques" vs. Ajuntament "districtes" — pick one canonical
  geography (or an explicit crosswalk) before joining any two of §2/§3/§4's tables.
- Force-jurisdiction reconciliation needed (§2.4 caveat): Mossos vs. Guàrdia Urbana vs. Policía
  Nacional recording responsibility, to avoid double-counting or under-counting when combining
  regional (Mossos/Idescat) and city (Ajuntament) series.
- None of §2's sources have been PDF/table-extracted yet — everything above is access-mechanism +
  headline-figure confidence only (per the confidence ratings inline), not yet primary-source-verified
  numbers in the sense `mir_informes_delitos_sexuales.md` achieves for the national sexual-crime
  series. Treat every number quoted above as **provisional, secondary-sourced (press coverage of a
  primary release)** until pulled from the primary table directly, consistent with C15.
