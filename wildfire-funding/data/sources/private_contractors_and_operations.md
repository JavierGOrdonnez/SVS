# Private contractors & operational resources — WFF

Second data dimension for this project, added 2026-07-28 after the euro-budget
approach hit a structural wall for several CCAAs (Madrid's case documented in
`SOURCES_INDEX.md`): what does each region actually deploy (personnel,
aircraft, vehicles), and who actually operates it — public corps, a
state-owned company, or a private contractor? This complements, not
replaces, `wff_spending.csv`/`wff_total_budget_timeseries.csv` — operational
counts don't tell you cost-effectiveness, but they're a genuinely comparable
metric where euro figures keep hitting scope/opacity walls.

Raw data: `data/raw/wff_operational_resources.csv` — one row per CCAA (13 of
17 covered so far; Cantabria, Castilla y León, País Vasco, Asturias have
partial fields where the source didn't disclose a figure). All rows
`confidence=low` — every figure is press-relayed from each region's own June
2026 seasonal-device announcement, not independently verified against an
official document (unlike the Madrid TRAGSA finding below, which is
primary-sourced). **Not yet covered**: Extremadura, Galicia, Ceuta, Melilla.

## Private-sector landscape (national)

Spain's wildfire response is not purely public. Three distinct private/mixed
mechanisms are documented:

1. **Aerial firefighting** — a small number of private operators hold most
   regional and national helicopter/aircraft contracts: **Avincis**
   (largest; contracts across Aragón, Galicia, Castilla-La Mancha,
   Andalucía, Comunitat Valenciana; one MITECO contract alone worth
   €44.7M, June 2025-Nov 2027), **Pegasus Aero Group** (Andalucía,
   Castilla-La Mancha, Castilla y León, Canarias — also holds a Madrid
   helicopter lot per `SOURCES_INDEX.md`), **Sky Helicópteros** (Baleares,
   Madrid, Extremadura), **Eliance Helicopter Global Services** (Madrid),
   **Martínez Ridao Aviación** (sole amphibious-aircraft supplier to six
   regions per one source).
2. **Ground brigades via state-owned "medio propio" companies** —
   principally **TRAGSA** (Empresa de Transformación Agraria, S.A.),
   legally a state-owned commercial company that regions can assign work to
   directly (an "encargo"/entrustment) without competitive tender, since it
   has the legal status of the administration's own instrumental resource.
   Madrid's TRAGSA entrustment is documented in detail below and in
   `SOURCES_INDEX.md`. Reported to handle ~40% of Castilla y León's
   ground-crew workforce too.
3. **Ground brigades via ordinary private contractors** — Castilla y León
   is the most heavily documented case: per a Público investigation, ~40%
   of its ground crews are split across roughly 20 private companies
   (named: Demontes €15.05M, Integra €10.37M, Acciona Medio Ambiente
   €11.66M, Foresa €4.67M, Inforest €3.84M, Eulen €2.21M, and others),
   totalling ~€108-110M/year. Only ~20% of Castilla y León's workforce is
   directly public.

**Not independently verified this pass** (all from a single Haiku research
agent's search pass, not fetched/read directly — treat as leads, re-verify
before citing as fact):
- Público, "El oligopolio que controla la extinción con medios aéreos se
  embolsa otros 400 millones":
  https://www.publico.es/politica/oligopolio-controla-extincion-medios-aereos-embolsa-otros-400-millones-comunidades-castigadas-fuego.html
- Público, "El negocio del fuego en Castilla y León: Mañueco reparte 110
  millones entre una veintena de empresas":
  https://www.publico.es/politica/investigacion-negocio-fuego-castilla-leon-manueco-reparte-110-millones-veintena-empresas.html
- El Diario, wage-disparity piece (€1,171/month Castilla y León vs.
  €3,600/month Catalonia for the same job category):
  https://www.eldiario.es/economia/1-170-euros-castilla-leon-3-600-euros-catalunya-desigualdad-salarial-bomberos-forestales_1_12554516.html
- Newtral, "Alquilar helicópteros y equipos privados para extinguir
  incendios cuesta al Gobierno más de 50 millones al año" — cites a
  three-year (2025-2027) national contract total of €156.4M:
  https://www.newtral.es/incendios-euros-dinero-gobierno/20250902/

## "Cartel del Fuego" — 2025 corruption conviction

A real, adjudicated case (not just an investigation): **12 people
convicted in February 2025** for bribery, abuse of office, and
embezzlement (sentences of 6 months to 2.75 years), for running a
geographic-division cartel ("Grupo 6") that rotated public aerial-
firefighting contracts among themselves to simulate competition over
~20 years. Companies named as implicated: Avialsa, Grupo FAASA, Taexsa,
Martínez Ridao Aviación, Trabajos Aéreos Espejo, CEGISA, Babcock Mission
Critical Services España. Estimated scheme value: over €151M. Convicted
companies received 9-month public-contracting bans (Feb 2025). One
source claims some banned firms may have circumvented the ban since —
**not independently verified this pass**, flag before citing.
Reference: https://es.wikipedia.org/wiki/Cartel_del_Fuego (verify against
primary court records before treating as more than a lead).

## CNMC investigation, opened January 2026 — ongoing, unresolved

Spain's competition authority (Comisión Nacional de los Mercados y la
Competencia) opened a **preliminary inspection into Avincis, Pegasus, and
Eliance** (Jan 27-30, 2026) for suspected cartel/bid-rigging behavior in
emergency aerial services (firefighting, medical transport, search &
rescue) — potential fines up to 10% of turnover if confirmed. **No
sanctioning process has started; this is an open investigation, not a
finding of guilt** — report accordingly. Lead source (not independently
fetched/verified this pass):
https://www.eleconomista.es/transportes-turismo/noticias/13753692/01/26/la-cnmc-investiga-a-avincis-pegasus-o-eliance-por-un-posible-cartel-en-el-sector-aereo-de-emergencias.html

## Madrid / TRAGSA — the one primary-sourced finding in this file

Everything above came from a single research pass and needs
re-verification before being treated as settled fact. This one is
different: obtained and read the actual official document.

**Document**: "ENCARGO A LA EMPRESA DE TRANSFORMACIÓN AGRARIA, S.A., S.M.E.,
M.P., (TRAGSA) PARA EL SERVICIO DE PREVENCIÓN Y APOYO A LA EXTINCIÓN DE
INCENDIOS FORESTALES E INCLEMENCIAS INVERNALES DE LA COMUNIDAD DE MADRID" —
signed by Carlos Novillo Piris, Director de la Agencia de Seguridad y
Emergencias Madrid 112, on behalf of the Consejero de Justicia, Interior y
Víctimas. Obtained via a Newtral FOI request (a redacted/"censurado" copy —
personal-data codes blacked out, and, separately, the 2023/2024/2025 annual
euro breakdown is also blank in this copy, whether redacted or an
extraction artifact wasn't determined). PDF:
https://www.newtral.es/wp-content/uploads/2025/08/01._encargo_censurado_nmf_firmado.pdf
(blocked WebFetch with a 403 — fetched successfully via `curl` with a
standard browser User-Agent instead).

**What it says, verbatim facts extracted**:
- Total entrustment value: **€107,066,036.90**, covering **47 months, 1
  February 2022 – 31 December 2025**.
- Legal basis: Article 32 and Disposición Adicional Vigésimo Cuarta of Ley
  9/2017 (Ley de Contratos del Sector Público) and Real Decreto 69/2019 —
  the legal regime that lets Madrid assign this work directly to TRAGSA
  without competitive tender, since TRAGSA is legally the administration's
  own "medio propio instrumental y servicio técnico."
- Co-financed by FEADER (Fondo Europeo Agrario de Desarrollo Rural) — an
  EU rural-development fund, meaning part of this is EU money, not purely
  regional.
- **Explicit budget address**: "se imputará con cargo al subconcepto 22706
  del programa 134 A 'Emergencias' del Presupuesto de Gastos de la
  Comunidad de Madrid." This is the same subconcepto found independently in
  the official 2026 `gastos-por-programa` Excel export (see
  `SOURCES_INDEX.md`'s round-2 Madrid finding): `22706: TRABAJOS REALIZADOS
  POR OTRAS EMPRESAS: ESTUDIOS Y TRABAJOS TÉCNICOS`, €31.3M for 2026 —
  a generically-labeled line that gives no hint from its name alone that
  it's the wildfire-brigade payment, which is exactly why the earlier
  keyword search (`grep "incendio"`) missed it. Two independent primary
  sources now cross-confirm the same budget address.
- Disclosed annual breakdown (partial — see caveat above): **2022 (10
  months, Feb-Nov): €23,708,728.30**. 2023/2024/2025/2026(1 month) figures
  are blank in this copy — not fabricated or estimated here; only the
  disclosed total (€107,066,036.90) and the one disclosed year are used in
  `wff_spending.csv`.
- A successor contract from 2026 onward is reported elsewhere (not in this
  document) to exceed €32M/year, with 425+ personnel being converted from
  temporary to permanent status — see `SOURCES_INDEX.md`'s TSJM section for
  the sourcing on that figure.

**Why this matters methodologically**: it overturns the strong version of
the earlier "Madrid doesn't isolate wildfire spending" finding. The truer
statement is: *Madrid's wildfire-brigade spending exists as a specific,
identifiable budget line — you just can't find it by searching for
"incendios" in the label, because it's booked as a generic administrative-
services subconcepto within the general Emergencias program, and only the
underlying entrustment document (not the budget itself) names what it's
actually for.* This is a real, demonstrated case of the "unreported not
necessarily intentionally, but structurally" pattern flagged by the user —
worth checking whether other CCAAs' TRAGSA (or equivalent medio propio)
entrustments follow the same pattern before concluding Madrid is unique.

## Strategic assessment (Opus think-through, partial — session-limited before final synthesis, mined from its transcript via a second agent)

Commissioned specifically to think through, not execute, where better data could
come from. Killed by a session/API limit before producing its planned final
write-up, but had already done substantial real research. Extracted findings:

**Diagnosis — why budget granularity fails, generalized beyond Madrid**:
IGAE (the state audit/accounting body) does publish national COFOG
(Classification of the Functions of Government) data classifying fire
services under code 03.2, 1995-2024 — but only at the **national aggregate**
level, not broken out per-CCAA. Spain's presupuestación funcional
(functional budget classification) structurally blends fire services into
broader "Public Order & Safety"/"Emergencias" categories at the regional
level too — Madrid's case (documented above) isn't an anomaly, it's the
norm. **Ley 5/2024** (the Forest Firefighters Act, establishing professional
standards for the profession) does not impose any national registry or
minimum staffing/resource *reporting* requirement on regions — so there's
no legal driver pushing CCAAs toward comparable disclosure. The agent's
read: the opacity is "partly structural (classification), partly
administrative design (no mandated transparency), and partly intentional
(avoiding scrutiny of private outsourcing)" — i.e., some mix of all three
of the possibilities the user raised, not cleanly one or the other.

**The single most promising lead surfaced**: **Civio's "España en llamas"
project** (civio.es, running since 2012, still updated — most recently
2026-07-09) and its underlying open dataset at
`https://datos.civio.es/dataset/todos-los-incendios-forestales/`. This is
a 28.3MB CSV, **1968-2023, derived from EGIF** (the official Estadística
General de Incendios Forestales, MITECO's national fire-report system,
150+ fields per incident) that Civio has already cleaned and republished
with **17 fields per fire including personnel deployed, terrestrial/aerial
equipment used, AND "Gastos de extinción asociados al incendio"
(extinction expenses in EUR) per fire** — i.e., real per-incident
resource-and-cost data across the whole country, aggregable to
CCAA×year. Known limitations (Civio's own disclosure): cause is "assumed"
in 76%+ of records (irrelevant to our use), precise geolocation missing
for ~51-54% of post-1983 fires, **19% of records lack extinction-cost
data and 34% lack economic-loss data** — incomplete, but far more
comprehensive than anything assembled by hand this session. **Not yet
downloaded**: the dataset page requires filling out a registration/email
form before download (confirmed via WebFetch and a direct `curl` — no
static download link found in the page HTML, the button is likely
JS-driven). This is Civio's own gating choice for a legitimate open-data
project, not a technical obstacle to route around — getting this dataset
is a real next step but needs a human to complete that form, not an
automated fetch.

Also separately, Civio has previously published cartel-concentration
findings in this same project (see below) and there's a general procurement
open-data route: **Plataforma de Contratación del Sector Público**
(`contrataciondelsectorpublico.gob.es`) publishes open, CPV-code-indexed
contract data since 2012, downloadable in bulk (XLSX); the aerial-firefighting
CPV code is reportedly **75251120** (aerial fire extinction services) —
same category of live, structured, primary official source as the Hacienda
Tier-1 parser already built this session, and a plausible template for a
similar parser if pursued.

**"Fire cartel" figures, a more rigorous version than the earlier pass
surfaced**: per Civio's own reporting (not yet independently re-fetched
this pass — flag before citing as final), the "Grupo 6" cartel ran
**2001-2021** (20 years, longer than the "~20 years" estimate from the
earlier search), manipulating **€277M+** in contracts — a materially
larger and differently-sourced figure than the "€151M" estimate from the
earlier Haiku pass, likely because Civio's count uses a more complete
contract set. Civio's reported per-region breakdown of manipulated-contract
value: **Castilla-La Mancha €72M, Extremadura €49M, Valencia/Cataluña
€47.5M, Andalucía €36.5M, Baleares €11M** — if this holds up on
re-verification, it's a genuinely useful CCAA-level split for the private-
contracting angle specifically. National total private aerial-firefighting
spend cited: **€384.61M (CCAAs) + €270M (national MITECO) = €654.61M**
for ~250 aircraft (period not confirmed — likely multi-year, needs
re-checking before use).

**Tractability ranking the agent had reached before being cut off**:
1. **Private-contracting/procurement route — high tractability.** Structured, CPV-indexed, open data; Civio's own methodology is a proven template.
2. **Operational-capacity route — medium tractability.** Real per-region sources exist (regional dispositivo announcements, Galicia's PLADIGA reports specifically praised as detailed) but nothing centralized — would need per-region compilation, which is what `wff_operational_resources.csv` above already started doing by hand.
3. **Budget/COFOG route — low tractability nationally, but not dead per-region.** National COFOG is too coarse; individual CCAA presupuesto-por-programas documents remain the only route, and (per Madrid) may hide the real line under a generic subconcepto rather than omit it entirely — worth checking other regions for the same TRAGSA-style pattern before writing off a region's budget approach.

## Civio's EGIF dataset — pulled, verified, and it delivers (2026-07-28)

Both leads from the strategic assessment above were chased with dedicated
research passes. **This one came through, fully**:

- **Access**: no registration needed after all (the form on the dataset
  page is an optional newsletter signup, not a gate). Direct URL:
  `https://data.civio.es/espanaenllamas/fires-map/fires-all.csv` — fetched
  directly with `curl`, 32.8MB, confirmed HTTP 200. **296,839 individual
  fire records, 1968-2023**, fields: `id, superficie, fecha, lat, lng,
  idcomunidad, idprovincia, municipio, causa, causa_supuesta, muertos,
  heridos, time_ctrl, time_ext, personal, medios, gastos, perdidas`.
- **Critical data-integrity catch**: the research agent that first found
  this claimed `idcomunidad` followed standard INE CCAA numbering
  (Cataluña=10, Galicia=13, etc.) — **this is wrong**, verified by
  cross-referencing each code's most common `municipio` values against
  real place names (e.g. code 3's top municipios — Viana do Bolo, A
  Gudiña, Muíños — are all in Ourense province, so code 3 = Galicia, not
  "Asturias" as INE numbering would give). Built the correct mapping
  empirically for all 18 codes present (17 CCAAs + Ceuta; Melilla has zero
  forest-fire records, plausibly correct given its size). See
  `parsers/aggregate_civio_egif.py` for the verified mapping — **do not
  trust any other source's `idcomunidad` mapping for this dataset without
  re-verifying it the same way.**
- **Aggregated to `data/raw/wff_egif_incidents_by_ccaa_year.csv`** (921
  rows, all 18 codes x all years present) via
  `parsers/aggregate_civio_egif.py`. The raw 32.8MB file is NOT committed
  to this repo (too large, and it's a stable directly-refetchable URL) —
  the script documents the exact re-download command.
- **The genuinely important finding, beyond just "we got the data"**:
  `gastos` (extinction cost in EUR) is real, but **its reporting coverage
  has collapsed for most CCAAs over time** — this is itself a citable
  transparency-decline finding, not just a data-quality footnote. Checked
  every CCAA's last year with any nonzero `gastos` value: **Galicia,
  Andalucía, Aragón, and La Rioja are the only regions still reporting
  extinction costs to EGIF as of 2019-2022** (Galicia's coverage is
  especially strong recently: 99-100% of its fires have a cost figure in
  2020-2022, vs. 17-18% in 2018-2019 — a real jump in reporting quality
  worth investigating why). Every other region **stopped reporting
  `gastos` years or decades ago**: Castilla y León (last: 2014), Cantabria
  (2017), Asturias (2013), Castilla-La Mancha (2011), País Vasco (2014),
  Cataluña (1996!), Comunidad Valenciana (1999), Madrid (**1991**),
  Murcia (2004), Navarra (essentially never — 3 records total, 1989-2004).
  This directly corroborates — with hard national data, not just Madrid's
  case — the user's suspicion that "these things don't get reported... 
  making this comparison very complex." It's not just Madrid; it's most
  of the country, and it's gotten worse over decades, not better.
- **Concrete numbers this unlocks for the regions that do report**: e.g.
  Galicia 2020: 341 fires, €12.59M extinction cost, 99.7% coverage.
  Galicia 2022: 355 fires, €23.90M, 100% coverage. These are real,
  comprehensive, incident-level extinction-cost totals — a fundamentally
  different and arguably more meaningful figure than any budget-line
  presupuestado/liquidado pair, since it's actual money spent fighting
  actual fires, aggregated from the incident-report system itself rather
  than a budget document.
- **`personal`/`medios` units not yet confirmed**: values are far larger
  than plausible headcounts for single fires (e.g. 360 for one 14ha fire
  in 1968) — almost certainly a cumulative effort metric (person-hours,
  or personnel × days deployed) rather than a simple headcount. Not
  resolved this pass; check Civio's/EGIF's own field dictionary before
  treating `personal_units_sum`/`medios_units_sum` as comparable to the
  press-sourced headcounts in `wff_operational_resources.csv` — they are
  almost certainly NOT the same unit and should not be compared directly
  without confirming this.

## Public procurement (CPV) route — pulled, works, one correction needed

Also chased directly. **Real, working, no-registration access confirmed**,
with one important correction to the earlier lead:

- **The CPV code was wrong in the original lead**: 75251120 is *legal
  services*, not aerial firefighting. The correct code is **60442000**
  ("aerial forest-firefighting services") — not yet independently
  re-verified against the official CPV nomenclature list, but consistent
  across multiple sources found this pass.
- **PLACSP (Plataforma de Contratación del Sector Público) bulk data**:
  confirmed downloadable as ATOM/XML ZIPs, no auth, pattern
  `https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3_AAAAMM.zip`
  — not yet actually downloaded/parsed this pass (large files, CODICE XML
  schema, would need real parsing work — a natural next Tier-1-parser-
  style project if pursued).
- **TED (EU-level, contracts >€140k)**: confirmed searchable without
  registration. **One concrete, independently corroborated contract
  found**: a consortium led by **Avincis Aviation España S.A.U.**
  (+ Avincis Aviation Iberia S.L.U. + Avincis Aviation Technics S.A.U.)
  awarded **€319.2 million** by ASEMA (Agencia de Seguridad y Emergencias
  de Andalucía) for aerial wildfire-suppression support, **2026-2031**
  (TED Notice 266189-2026). Corroborated via a second independent search
  (spaintenders.com) beyond the original research agent's claim, though
  direct WebFetch of the TED notice page itself returned empty content
  (likely JS-rendered) — so this is corroborated-by-search, not read
  directly from the primary notice. **Real, unresolved discrepancy worth
  flagging**: the Junta de Andalucía's own Consejo de Gobierno
  authorization (2025-12-02, official press release) cites **€112 million**
  for "contratar helicópteros para el Plan Infoca" — a very different
  figure from the €319.2M TED total. These aren't necessarily
  contradictory (€112M could be an initial-year/partial authorization
  within the larger 2026-2031 contract ceiling) but this wasn't
  reconciled — don't cite either figure as "the" Andalucía aerial
  contract value without resolving this first.
- **Community-maintained parsed mirrors** were also surfaced (a GitHub
  repo claiming pre-parsed Parquet/CSV of PLACSP + TED + company-registry
  data, 2012-2026) — **not verified this pass**, treat as an unconfirmed
  lead, not a citable source, until someone actually checks the repo
  exists and contains what's claimed.

## Open questions / next steps

- ~~Download Civio's dataset~~ **Done** — see above, `wff_egif_incidents_by_ccaa_year.csv`.
- ~~Investigate PLACSP CPV route~~ **Done, access confirmed** — see above;
  actually downloading + parsing the bulk XML is the remaining work, not
  yet started (would be a genuine parser-building project, similar scope
  to `parsers/parse_hacienda_totals.py`).
- **New top priority**: confirm the `personal`/`medios` unit definitions in
  the EGIF/Civio data (person-hours? headcount-days? something else?) —
  blocks comparing them meaningfully to `wff_operational_resources.csv`'s
  headcounts.
- **New**: reconcile the Andalucía Avincis contract discrepancy (€112M
  Junta authorization vs. €319.2M TED total) before citing either figure.
- **New**: investigate *why* Galicia's `gastos` reporting coverage jumped
  from ~17-18% (2018-2019) to ~99-100% (2020-2022) — a real, specific,
  answerable question (a reporting-process change? a post-2020 policy?)
  that could matter for interpreting the whole EGIF cost series.
- Confirm whether other CCAAs also use TRAGSA (or their own regional
  equivalent — e.g. Galicia's SEAGA, mentioned in passing during earlier
  Galicia research this session but not investigated as an entrustment
  vehicle) for wildfire brigades, and whether the same "generic
  subconcepto hides a specific entrustment" pattern recurs.
- Re-verify the "not independently verified this pass" items above (Cartel
  del Fuego full case details, CNMC investigation status, the Público
  Castilla y León figures, the Newtral €156.4M national contract figure)
  by fetching the primary sources directly rather than trusting a single
  research pass's summary.
- Extend `wff_operational_resources.csv` to the 4 CCAAs not yet covered
  (Extremadura, Galicia — both otherwise well-covered in the euro data —
  plus Ceuta/Melilla if in scope).
- Investigate whether operational-resource counts (this file) correlate
  with the execution-rate findings already in `wff_spending.csv` (e.g. does
  Extremadura's 8.9%-executed line correspond to a region that under-
  delivered on announced personnel/aircraft too, or is the resource
  deployment real even when the specific investment project wasn't?).
