# Sources Index — WFF

Living index of sources found in an initial search pass (2026-07). Every
figure below is a lead, not yet verified against the primary budget
document per `../../SPEC.md` C1 — treat as `confidence=unverified` until
traced to the actual Ley de Presupuestos article or official report table.

## Official / primary sources

- **MITECO — Estadística General de Incendios Forestales (EGIF)**:
  https://www.miteco.gob.es/es/biodiversidad/temas/incendios-forestales/estadisticas-datos.html
  — national fire database (count, area burned), fed by CCAA reports via
  the national coordination center (CCINIF); not a funding source, but the
  denominator for "does more spending correlate with fewer/smaller fires."
  Preliminary annual reports ("Avance Informativo") also published, e.g.
  [Avance IIFF 2025](https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/incendios-forestales/Avance_IIFF_2025_.pdf).
- **Cuarto Inventario Forestal Nacional (IFN4)** — per-CCAA forest surface
  reports, published individually per region (e.g. Comunidad Valenciana,
  Madrid, País Vasco editions found via BOE/MITECO bookstore listings).
  Fieldwork not simultaneous across CCAAs — see SPEC.md C5/R2.
- **Ministerio de Hacienda — Informes de Presupuestos Generales de las
  CCAA**: `https://serviciostelematicosext.hacienda.gob.es/SGCIEF/PublicacionPresupuestos/aspx/MenuREP.aspx`
  — official portal for each CCAA's approved annual budget; needed for the
  total-budget denominator (C6). Confirmed via initial search that not
  every CCAA passes a new law every year (Cataluña extended its prior
  budget into 2024) — must be noted per C7.
- **INE — population by CCAA**: Estadística Continua de Población (ECP) /
  Censo Anual de Población (replaced the old Padrón Continuo series from
  2021 onward) — national total 49,128,297 as of 2025-01-01 per INE press
  note; per-CCAA breakdowns available through the same INEbase portal
  (`ine.es/dyngs/INEbase`).

## NGO / research-compiler sources (secondary, but source their own primaries)

- **ASEMFO (Asociación Nacional de Empresas Forestales) — "Estudio de
  Inversión en el Medio Forestal"**, XIII edition, covering 2005–2022 spend
  per CCAA. Found via a Verificat.cat writeup which itself cites this as
  primary. Gives normalized (€/hectare) figures for some regions, e.g.
  reported: Andalucía €1,143.6M total 2005–2022, Castilla-La Mancha
  €653.2M, Extremadura €294.4M, Cataluña €40.3M (low end); Navarra ~€12/ha
  (lowest per-hectare), Madrid ~€735/ha (highest). **Needs the actual
  ASEMFO PDF** ("Estudio XIII Inversión 2021-2022.pdf" per Verificat) to
  verify these before use — Verificat's numbers are a secondary relay.
- **Greenpeace España — "Grandes incendios forestales" (annual report)**:
  https://es.greenpeace.org/es/sala-de-prensa/comunicados/ — the key
  source for the prevention/extinction disclosure-gap finding: a 2023
  public-information request found only Galicia, Extremadura,
  Castilla-La Mancha, and Baleares publish a clear prevention/extinction
  split. Also source for the national aggregate trend: forest budget
  €1,742M (2009) → €1,295M (2022), a 26% drop; prevention-specific spend
  fell further, ~49.77% over the same window per a related Infobae
  writeup. 2025 season figures: 130,236 ha burned in "grandes incendios",
  extinction cost estimated €3,548–6,741M (wide range, needs the
  underlying methodology note).
- **Verificat.cat — "Prevención de incendios: radiografía de las CCAA"**:
  https://www.verificat.cat/es/prevencion-de-incendios-radiografia-de-las-comunidades-autonomas-en-la-lucha-contra-el-fuego/
  — fact-checker piece, normalizes by forest hectare (not by population or
  total budget), cites ASEMFO as primary; useful methodology reference,
  not itself a primary source.
- **Forescat.com — "Evolución del presupuesto en prevención y extinción de
  incendios en España (2000-2024)"**: https://forescat.com/evolucion-del-presupuesto-en-prevencion-y-extincion-de-incendios-en-espana-2000-2024/
  — candidate for the longest available national time series (T8); origin
  and underlying primary sources need verification before use.
- **Democrata.es — 2026 CCAA ranking**: reports 2026 approved figures
  (regional plans, mostly `no_desglosado` totals): Comunidad Valenciana
  €298.47M, Andalucía (Plan INFOCA) €271.6M, Castilla y León €222.7M,
  Galicia (Plan PLADIGA) €213M, Extremadura (Plan INFOEX) €116.8M,
  Asturias >€78M, Aragón (Plan INFOAR) >€54M, Madrid (Plan INFOMA) €52.5M.
  Useful as a same-year cross-CCAA starting point for T3, but trace each
  figure back to the region's own budget law before treating as
  `confidence=high`.
- **Fundación Civio — "Dónde van mis impuestos"**: https://dondevanmisimpuestos.es/ccaa
  — aggregates/visualizes CCAA budgets by category; worth checking whether
  it already breaks out a wildfire/medio-natural line usable for T6.

## Explicitly checked and found insufficient alone

- No single source (official or NGO) currently covers all 17 CCAAs × all
  years × a clean prevention/extinction split. R1 in SPEC.md tracks
  combining sources per-CCAA-per-year rather than picking one.

## Per-CCAA spend sources used in the first data pass (2026-07-27)

Coverage priority was explicitly widened over the prevention/extinction
split — see SPEC.md T1/C2 note. Each source below is cited per-row in
`data/raw/wff_spending.csv`'s `source_ref`/`notes` columns; most figures
have an unresolved conflicting alternate from a second source.

- **El Debate**, ["Así invierten las comunidades en la lucha contra los incendios" (2026-07-27)](https://www.eldebate.com/espana/20260727/asi-invierten-comunidades-lucha-contra-incendios-madrid-entre-presupuesto-proporcional-destina_443841.html)
  — the single best same-year cross-CCAA comparative source found: Andalucía, Galicia, Castilla-La Mancha, Asturias, Madrid, Murcia, Cantabria, La Rioja. Explicitly notes regions don't use comparable budget category boundaries.
- **Demócrata**, [ranking piece (2026)](https://www.democrata.es/politicas/comunidades-mas-invierten-en-incendios-forestales-ranking-gasto-en-espana-en-2026/) — Comunidad Valenciana, Extremadura, Aragón, Castilla y León (conflicts with El Debate's Andalucía/Galicia figures by ~10%, unresolved).
- **Castilla-La Mancha regional government**, [official press note](https://www.castillalamancha.es/actualidad/notasdeprensa/el-gobierno-regional-invertir%C3%A1-126-millones-de-euros-en-prevenci%C3%B3n-y-extinci%C3%B3n-de-incendios) — 126M for 2026 (Plan INFOCAM); this is the one row sourced directly to an official regional-government statement rather than press aggregation, hence `confidence=medium` not `low`.
- **zuk.eus** (Diputación de Álava coverage) — País Vasco's three diputaciones forales (Bizkaia, Álava, Gipuzkoa) each publish their own figure; summed to 100.2M but this bundles general firefighting/rescue, not wildfire-only — a real example of the "different administrations, different category boundaries" problem flagged in README.md.
- **ecoticias.com / palmesana.com** — Islas Baleares, prevention-only partial figures (IBANAT + FOGAIBA), no consolidated total found.
- **Crónica Global** — Cataluña's 2026 device (18M) plus a separate 5-year, 15M/year firebreak-strip program not folded into that figure.
- **Regional press coverage** — Navarra (42.7M, explicitly caveated as including general firefighting, not wildfire-specific), Cantabria (own Plan de Incendios Forestales cites 8.4M for 2025, a much narrower figure than El Debate's 26.3M for the same region).
- **Canarias**: no consolidated regional total found — wildfire competencies split between Gobierno de Canarias and each cabildo insular; only fragment found was Gran Canaria's own cabildo (~5M Céntimo Verde Forestal + 6M own funds, 2026). Documented as a gap, not filled with a guess.

## Denominator sources used

- **Population**: `es.wikipedia.org/wiki/Anexo:Comunidades_y_ciudades_autónomas_de_España`, itself relaying INE's Censo Anual de Población 2024 (1 Jan 2024 snapshot) — all 17 CCAAs + Ceuta/Melilla.
- **Forest area**: MITECO, *Anuario de Estadística Forestal 2019*, chapter 6 ("Gestión Forestal Sostenible"), table 6.1.1 — direct PDF at
  `https://www.mapa.gob.es/estadistica/pags/anuario/2019/CAPITULOSPDF/CAPITULO06/pdfc06_1.1.pdf`, extracted with `pdfplumber` (see `analysis/compute_normalized.py`'s data prep). All 17 CCAAs, `TOTAL FORESTAL` column, hectares converted to km².
- **Total CCAA budget (initial/approved, 2025/2026)**: sourced per-region from press coverage of each budget law's approval (regional-government sites, BOE citations where found, and regional press) rather than from Hacienda's own portal (`serviciostelematicosext.hacienda.gob.es` is a JS-driven query tool WebFetch couldn't drive this pass — worth a direct-CSV retry). 15 of 16 spend-covered CCAAs populated; Canarias not sourced (no wildfire figure either). Per-row citations and approval-stage tags (`aprobado_definitivo`/`proyecto`/`proyecto_convalidado`) are in `wff_denominators.csv`.

## Recovered-from-cache rows (2026-07-28) — presupuestado/liquidado pairs, source_ref pending re-verification

A batch of Tier-2 background research agents crashed mid-run (environment
proxy outage) before committing anything, but their downloaded/extracted
research artifacts survived in the session scratchpad and were recovered
and hand-verified before writing into `wff_spending.csv`. Each of the 9
rows below is `confidence=low` specifically because the exact live URL for
its source document hasn't been re-fetched/confirmed this pass (the
content itself was read directly from the cached document, not
guessed) — re-verifying and filling in `source_ref` is the natural
next step for each:

- **Galicia 2023, presupuestado** (4 rows): from the Memoria do proxecto
  de Lei de Orzamentos da Xunta de Galicia 2023, Consellería do Medio
  Rural, page 103 — 4 named wildfire-related capital-investment lines
  (Prevención de danos..., Mellora do operativo..., Silvicultura de
  prevención..., Recuperación integral do territorio...). These are a
  **partial slice** of PLADIGA (capital-investment sub-programs only,
  excludes running/personnel costs which sit elsewhere in the budget) —
  do not compare their sum directly to the existing lumped PLADIGA press
  figures (190-213M for 2026) without accounting for that gap.
- **País Vasco / Diputación Foral de Bizkaia 2023** (2 rows): from
  Bizkaia's own open-data budget-execution extract, project code
  `2022/0121` "Medidas contra incendios forestales" — a real,
  concrete presupuestado-vs-liquidado gap: crédito inicial €0 (not in the
  originally-approved budget) vs. obligación reconocida (executed)
  €1,340,946, funded entirely via in-year credit modification. Bizkaia
  only — one of the 3 diputaciones forales, not comparable in scope to
  the existing full-País-Vasco 2025 row.
- **Cataluña 2020-2021** (3 rows): from the Compte General de la
  Generalitat de Catalunya, exercici 2021 — functional program
  **223 "Prevenció, extinció d'incendis i salvaments"**: crèdits inicials
  237.48M (2021), obligacions reconegudes 253.10M (2021) and 212.87M
  (2020, from the same document's YoY comparison table). This program is
  Cataluña's general Bombers corps (urban + wildfire response together,
  same corps handles both) — broader scope than wildfire-only, treat as
  a ceiling.

## Sequential foreground pass, round 2 (2026-07-28)

Per user direction: dropped the parallel-background-agent approach (see
the recovered-from-cache section above for why) in favor of working
CCAAs one at a time in the foreground. Order and outcome:

- **Extremadura**: landed 5 rows (2024) from the eldiario.es article
  already in this index — 2 real presupuestado/liquidado pairs (40.8% and
  8.9% execution) plus one presupuestado-only narrow line.
- **Comunidad de Madrid — round 2, intensified (2026-07-28)**: found the
  actual official budget-by-program data source: Madrid publishes its full
  presupuesto in structured XLSX at
  `https://www.comunidad.madrid/docs/assets/2025/12/26/2026-presupuesto-gastos-por-programa-partida.xlsx`
  (fetched directly, 9,868 rows, every program × chapter × subconcepto for
  2026) plus a parallel "Ejecución y Liquidación" PDF book (Libro 08,
  92 pages — but broken down by sección/centro presupuestario, not by
  programa, so not usable at the granularity needed).
  **Definitive structural finding**: inspected every one of Madrid's ~100
  budget programs by name — **there is no "incendios forestales" or
  INFOMA-named program at all**. Wildfire-related spending is genuinely
  split across program `456A` (Biodiversidad y Recursos Naturales, 51.4M
  for 2026 — includes reforestation/forest-maintenance line items but not
  fire-specific) and program `134A` (Emergencias, 280M — Madrid's general
  Bomberos/emergency corps, far too broad to use). Neither program's
  line-item detail (checked down to the `Subconcepto` level) contains an
  "incendios" label anywhere. The 52.7M INFOMA figure the Consejería
  announces each summer is a cross-program operational estimate the region
  itself computes, not a single traceable budget line — this is why every
  search this session (and the prior background-agent attempt) came up
  empty on a clean presupuestado/liquidado pair for Madrid specifically.
  Added program `456A`'s 2026 total as the closest available context row
  (`confidence=low`, `coverage=partial`, clearly caveated).

  **Madrid — round 3, journalistic leads (2026-07-28, per user request to trace secondary/press investigation)**:
  the user's original cue for this whole project was the 2026 fire season, so
  went looking specifically for investigative press on Madrid's fire-service
  funding under the current government. Found a real, court-adjudicated
  finding — not just an allegation — with a clean, well-corroborated timeline:

  - **2023-12-19**: firefighters' union (CSIT Unión Profesional) files a
    formal complaint with the Consejería de Economía, Hacienda y Empleo,
    citing a prior Tribunal Supremo ruling that the mandatory insurance
    surcharge funding fire services (5% on fire policies + 2.5% on
    multi-risk policies, collected nationally via UNESPA/Consorcio de
    Compensación de Seguros and redistributed to regional/local fire
    services by law) "can only be dedicated to improving prevention and
    firefighting services" — alleging ~€40M of these earmarked funds,
    2019-2023, were instead spent on unrelated budget items.
    (publico.es, 2023-12-19: https://www.publico.es/sociedad/bomberos-comunidad-madrid-denuncian-gobierno-ayuso-desviar-40-millones-aseguradoras.html)
  - **2026-01-13**: the Tribunal Superior de Justicia de Madrid (TSJM)
    **rules in the firefighters' favor**, confirming the diversion and
    ordering the funds be used "íntegramente" (in full) for "inversión
    real" (capital investment) in the Servicio de Prevención, Extinción de
    Incendios y Salvamento (SPEIS) — not for "gastos de renting" (vehicle
    leasing) or other current-expense budget items, which is what the
    money had actually been spent on.
    (infobae.com, 2026-01-13: https://www.infobae.com/espana/2026/01/13/la-justicia-avala-la-denuncia-de-los-bomberos-la-comunidad-de-madrid-desvio-40-millones-que-debian-invertirse-en-proteccion-contra-incendios/;
    corroborated independently by mediadoresseguros.madrid, an insurance-industry
    trade outlet with no political stake:
    https://mediadoresseguros.madrid/el-tsjm-da-la-razon-a-los-bomberos-los-40-millones-aportados-por-unespa-deben-ir-integramente-a-inversion-real/)
  - **2026-07-28**: the ruling resurfaces in press coverage of the current
    (worst-on-record, per Ayuso's own characterization) fire season, with
    the firefighters' union explicitly linking the historical diversion to
    present capacity gaps — over 40 vehicles out of service, shortages of
    aerial ladders and specialized rescue trucks.

  **Scope caveat, same as the 134A finding above**: SPEIS is Madrid's
  general fire/rescue corps (urban + wildfire together), not a
  wildfire-isolated fund — but this is arguably the single most important
  qualitative finding for Madrid in this whole dataset: an **adjudicated**
  (not merely alleged) 5-year pattern (2019-2023) of a legally earmarked
  firefighting-investment funding stream being diverted to cover operating
  costs instead, under the current government, now resurfacing amid a
  historic fire season. Not added as a `wff_spending.csv` row — the €40M
  figure is a 5-year cumulative total with no disclosed annual breakdown,
  and covers a specific earmarked *funding stream* rather than a
  program-year budget line, so it doesn't fit this dataset's
  (ccaa, year, program) grain without fabricating a split. Documented here
  instead as the strongest lead for anyone extending Madrid's coverage.

  **Tracing the legal/documentary chain behind the ruling (2026-07-28,
  per user request)** — what official documents does this case actually
  rest on:

  - **The underlying mechanism**: a **5% surcharge on fire-insurance
    premiums** (recargo), collected by insurers and passed to whichever
    public administration actually maintains the fire-prevention/
    extinction/rescue service in a given area — municipalities that have
    assumed the service themselves, or the region where they haven't.
    Distinct from the separate, better-known Consorcio de Compensación de
    Seguros surcharges (extraordinary-risk cover, motor-liability cover)
    established in Real Decreto Legislativo 7/2004 (BOE-A-2004-18910,
    "Estatuto Legal del Consorcio de Compensación de Seguros") — this
    fire-service recargo is regulated separately, apparently at the
    regional/local level ("normativas autonómicas" per the sources
    checked). For Madrid specifically, the SPEIS itself is established by
    regional law **Ley 14/1994, de 28 de diciembre, por la que se regulan
    los servicios de prevención y extinción de incendios y salvamentos de
    la Comunidad de Madrid** (BOE-A-1995-8732:
    https://www.boe.es/buscar/doc.php?id=BOE-A-1995-8732) — the most
    likely home for the specific recargo-earmarking article, though the
    exact article number wasn't pinned down this pass (would need to read
    the full law text, not yet done).
  - **The national precedent**: a **Tribunal Supremo ruling, November
    2020**, establishing that recargo funds must be spent "única, íntegra
    y exclusivamente" (solely, fully, exclusively) on real investment in
    the fire service — cited by every regional ruling found. Exact
    case/ECLI number not pinned down this pass.
  - **This is not a Madrid-only pattern** — the same legal fight has
    played out in at least two other regions, both independently found:
    **Asturias/Gijón** (TSJ Asturias ruling, ratifying a case initiated
    in 2015, ordering ~€1.5M invested) and **Cantabria** (TSJ Cantabria,
    notified 2024-09-02, over a disputed €3.7M of €7.4M collected
    2018-2022, per eldiariotorrelavega.es:
    https://www.eldiariotorrelavega.es/articulo/cantabria/justicia-condena-gobierno-cantabro-obliga-invertir-37-millones-pendientes-servicios-bomberos/20240911202326035079.html).
    This turns Madrid's case from an isolated political story into one
    instance of a recurring, litigated national compliance problem —
    worth knowing if this line of inquiry gets extended to other CCAAs.
  - **The evidence base for Madrid's specific complaint**: per the
    union's own 2023-12-19 press release (CSIT, cited in the timeline
    above), their complaint rests on noticing that **the corresponding
    budget line disappears/changes pattern across Madrid's own published
    annual Presupuestos, 2019-2023** — not a leaked internal document.
    That means this is independently re-traceable through the same public
    budget documents already being used elsewhere in this project (the
    `Libro 11`/`gastos-por-programa` files already fetched for the round-2
    structural finding above) — a natural next step if this thread gets
    picked back up, though which exact line/program the recargo revenue
    and its offsetting investment appear under was not identified this
    pass (the revenue side wasn't searched — only expenditure-side
    "primas de seguros" lines were checked, which is Madrid paying
    premiums on its own assets, the wrong direction; the recargo is
    revenue Madrid *receives*, not pays).
  - **Not found this pass**: the exact TSJM sentencia number/ECLI (CENDOJ,
    the judiciary's public case database at poderjudicial.es, has a
    search form for this but it requires interactive form submission that
    WebFetch can't drive — a live session could search it directly), and
    the Comunidad de Madrid government's own response/rebuttal, if any
    (no source found quoted an official reaction).

  **Also found, not yet independently verified**: press claims that the
  2026 INFOMA operational scheme cut per-crew staffing from 7 to 5
  firefighters (unions' claim, reported by El Plural, not corroborated
  against an official document this pass) and a comparison piece
  (bilbaohiria.com, 2026-07-25) contrasting the 52.7M INFOMA figure against
  the 83.2M Madring/F1-circuit construction cost — explicitly an
  opinion/critical-framing piece, not a budget-execution finding, cited
  here only as a lead, not a fact.

- **Aragón**: real search effort (Cámara de Cuentas, a Cortes de Aragón
  written parliamentary answer fetched directly) — found only vague
  multi-year policy commitments (e.g. "€400M for the Strategic Plan"
  spanning several years), nothing at the annual presupuestado/liquidado
  grain this dataset needs. Documented as a gap.
- **Castilla-La Mancha**: no new material found beyond what's already in
  the dataset (2025/2026 official press-release figures).
- **Castilla y León**: landed a strong pair — theobjective.com
  (2025-08-14) reported the region's own mid-year ejecución presupuestaria
  showing only 48.5% of the 104.3M "Programas de Prevención y Extinción
  de incendios" budget executed as of 1 June 2025, weeks before that
  year's severe fire season. Explicitly an interim, not year-end, figure.
- **Galicia (deepen)**: mined the same Memoria-do-proxecto-de-Lei-de-
  Orzamentos source (already used for the 2023 rows) for 5 more years —
  2019, 2020, 2021, 2024, 2025 — recovered from the session's research
  cache. 19 more rows, all partial investment-line slices, presupuestado
  only. Gives Galicia the deepest year-over-year series in the dataset.

## Sequential foreground pass, round 3 (2026-07-28) — current wildfire crisis, Ávila & Madrid

Per user request: moved from budget-line micro-data to journalistic/research coverage
of the actual July 2026 wildfires in Ávila and Madrid, focusing on resources deployed
by each CCAA and the broader funding context.

### The fires (as of 28 July 2026)

Two fires treated as one single incident by the Government, declared emergencia de interés
nacional. Combined perimeter ~280 km, >77,000 ha affected across both regions + Toledo
(Castilla-La Mancha, downgraded to nivel 2 on 28 July).

- **Ávila** (Castilla y León): ~50,000 ha — "el mayor incendio y el más agresivo de la
  historia de España" (EL PAÍS, 2026-07-28). 16 municipalities evacuated, 3 confined.
  ~25,087 people evacuated. Origin: person using machinery in a prohibited area (one
  arrested, one investigated).
- **Madrid**: ~34,000 ha (Ayuso's figure, 28 July; Interior had been reporting ~25,000).
  12 municipalities evacuated, 4 confined. ~31,865 evacuated, ~19,262 isolated at home.
  Critical zone: río Cofio / pantano de San Juan, where both fires nearly confluent.
- **National total**: 173,651 ha forest land burned year-to-date (MITECO, via EL PAÍS).
  EFFIS satellite estimate: 157,501 ha (higher than MITECO's slower CCAA-compiled figure).
- 47 roads cut (Ávila, Castellón, Madrid, Toledo provinces).
- EU Civil Protection Mechanism activated: Turkey sent 2 Air Tractor Fireboss (to
  Burgohondo, Ávila); Italy and Greece sent additional aircraft. Portugal sent 100+
  military personnel to Ávila.

Sources:
- EL PAÍS, "Carrera contra el fuego en Ávila y Madrid: 24 horas clave" (2026-07-28):
  https://elpais.com/espana/2026-07-28/carrera-contra-el-fuego-en-avila-y-madrid-24-horas-criticas-antes-de-la-ola-de-calor.html
- EL PAÍS, directo (2026-07-28):
  https://elpais.com/espana/2026-07-28/ultima-hora-de-los-incendios-forestales-en-directo.html
- Europa Press, despliegue (2026-07-25):
  https://www.europapress.es/sociedad/noticia-desplegados-mas-2700-efectivos-426-medios-terrestres-gobierno-incendio-madrid-avila-20260725145330.html
- EFE (2026-07-25): https://efe.com/espana/2026-07-25/espana-gobierno-despliega-efectivos-terrestres-aereos-incendio-madrid/
- masdiario.es (2026-07-26): https://masdiario.es/el-despliegue-de-la-ume-que-combate-el-fuego-en-madrid-y-avila/
- Europa Press, medios aéreos Turquía (2026-07-26):
  https://www.europapress.es/sociedad/noticia-espana-recibira-dos-aviones-turcos-extincion-incendios-suman-medios-aereos-grecia-italia-20260726113222.html
- Diario de León / ICAL (2026-07-28):
  https://www.diariodeleon.es/castilla-y-leon/260728/2092524/incendio-avila-sigue-control-3-000-profesionales-tres-frentes.html

### State-level deployment (Gobierno central) to the Ávila+Madrid fires

Headline (Europa Press, 25 July): **2,737 efectivos, 426 medios terrestres, 21 medios aéreos**.

Full breakdown per the Gobierno's own balance:
- **UME**: 1,201 intervinientes, 405 medios terrestres
- **Guardia Civil**: 1,085 agentes, 60 vehículos, 2 helicópteros (later updated: 1,807
  agentes, 69 vehículos, 4 helicópteros per masdiario.es 26 July)
- **Policía Nacional**: 220 agentes, 1 helicóptero
- **Protección Civil**: 110 efectivos
- **MITECO**: 103 personas, 4-5 BRIF, 11 aviones, 8 helicópteros, 1 UMAP (Unidad Móvil
  de Análisis y Planificación)
- **CSIC**: 18 investigadores asesorando
- Later (26 July): totals updated to >3,400 efectivos, 23 aeronaves MITECO, 405 medios
  terrestres UME

### Madrid (Comunidad de Madrid) — INFOMA 2026 resources

**IMPORTANT — re-audit (2026-07-29)**: the 6,110 figure below is the ENTIRE
INFOMA civil-protection plan (general Bomberos urban+forest, Protección Civil
volunteers, forest agents, Madrid 112). Wildfire-DEDICATED forces are substantially
smaller. See corrected breakdown in `wff_operational_resources.csv` line 15
(`confidence=unverified`). Key corrections:
- The "1,700 bomberos forestales" label (Europa Press 2026-06-20) = the same 1,680
  general Bomberos corps (urban + forest), NOT wildfire-dedicated forest brigades.
- Actual wildfire-dedicated: ~419-450 TRAGSA-managed bomberos forestales (year-round),
  ~61 public-sector bomberos forestales (currently INACTIVE due to labor dispute),
  ~220 seasonal hires. Total: ~700-730, minus 61 inactive. See row 15 for full caveats.
- The 10 helicopters serve the entire INFOMA (including urban), not exclusively wildfire.
- The "571 efectivos diarios in extinction" figure (published by Comunidad in INFOMA
  announcement) is the Comunidad's own estimate of daily on-duty extinction personnel
  across ALL fire services — but the union claims forest-dedicated units in 19 parks
  had a firetruck + 2-3 crew in prior years vs zero in 2026 (EL PAÍS, 2026-07-26).

Published 2026-06-12 (pre-season) by Consejería de Medio Ambiente, Agricultura e Interior:
- **Budget**: €52.7M (+3.5% vs 2025). Described as "cifra récord." Madrid claims to be
  the European region with highest per-hectare investment.
- **Personnel**: 6,110 professionals + volunteers (+2.3% vs 5,970 in 2025). Includes
  1,680 Bomberos + 350 Agentes Forestales + 3,420 Protección Civil volunteers (113
  local groups) + 180 Madrid 112 professionals. 571 efectivos diarios in extinction.
  Plan Forestal 2026-2030: €160M total over the period, ~€52.8M (10M+/year) for
  prevention specifically.
- **Aircraft**: 10 helicopters (8 helipads), of which 3 lots contracted to SKY
  HELICÓPTEROS, ELIANCE, PEGASUS respectively
- **Vehicles**: 27 heavy pumps (bombas pesadas), 8 water tanker trucks (camiones
  nodriza), 49 4x4 transport vehicles, 2 mechanized units
- **Infrastructure**: 22 fire stations, 25 forest brigade stations, 17 heavy pump
  stations, 38 watchtowers, 4 cameras, Grupo Especial de Drones
- **History**: Since 2019, investment +38%, INFOMA personnel +23.5%.
- **Deployed to the current fire** (Ayuso, 28 July): 300 regional firefighters/bomberos
  forestales + agentes forestales, 50 ground vehicles, 10 aircraft. Additionally,
  ≈400 efectivos (Delegado del Gobierno, 28 July) worked the río Cofio line overnight.

Sources:
- La Razón, "INFOMA 2026: 52 millones de euros y 6.100 efectivos" (2026-06-12):
  https://www.larazon.es/madrid/infoma-2026-52-millones-euros-6100-efectivos-lucha-fuego_202606126a2bf81bf2a09b63649d0dbf.html
- Europa Press, "Comunidad invierte más de 52,7 millones" (2026-06-12):
  https://www.europapress.es/madrid/noticia-comunidad-invierte-mas-527-millones-campana-contra-incendios-forestales-eleva-operativo-6110-efectivos-20260612133851.html
- El Periódico (2026-07-27): https://www.elperiodico.com/es/politica/20260727/comunidad-madrid-destina-52-7-132851630
- Europa Press (2026-06-20): https://www.europapress.es/madrid/noticia-comunidad-tomo-nota-incendios-ano-pasado-disenar-plan-infoma-1700-bomberos-mas-formacion-20260620093950.html
- El Diario de Madrid (2026-06-12): https://www.eldiariodemadrid.es/articulo/medio-ambiente/madrid-prevencion-lucha-incendios-forestales/20260612125940133780.html
- madridinforma.eldiario.es (2026-06-17): https://madridinforma.eldiario.es/madrid-activa-la-epoca-de-alto-riesgo-de-incendios-forestales-con-6-110-efectivos/
- Orden 1471/2026, BOCM (2026-04-29), approving the Plan Anual de Prevención, Vigilancia y Extinción de Incendios Forestales 2026:
  https://bocm.es/boletin/CM_Orden_BOCM/2026/04/29/BOCM-20260429-23.PDF

### Castilla y León (Ávila) — INFOCAL 2026 resources

Published in multiple sources (Junta de Castilla y León, pre-season announcements, Cortes
appearances, Plan Anual 2026 published in BOCYL):
- **Budget headline (January 2026)**: €169.63M total for prevención y lucha contra incendios
  forestales, of which €151M chapters VI+VII (investment), €16M personnel (after extending
  fijo-discontinuo to full-year), €2.63M to Consejo Comarcal del Bierzo. Later press
  summaries (June 2026) cite ~€160M for the operativo alone — scope discrepancy likely
  due to budget year timing (prorogation of 2024 budgets with modifications).
- **Personnel**: 5,075 professionals (+355 vs 2025), of which 837 puestos fijos-discontinuos
  converted to fijos in Dec 2025. 129 ground teams (of which 49 transitioning to Tragsa),
  24 helitransported teams (ELIF), 16 night teams (5 months), 163 watchtower posts. 9 UBA
  (Unidad de Brigada y Autobomba) units.
- **Aircraft**: 26 helicopters + 1 ACT (air cargo truck). Plus MITECO contribution: 6 helis,
  2x 5,000L amphibious, 2x 3,500L amphibious, 1 ACO (coordination/observation). 24
  ELIF-equipadas helibases during peligro alto.
- **Ground vehicles**: 94 own fire trucks (autobombas, >3,000L tanks), 28 with night crews
  year-round; 30 reserve trucks (2025 campaign); 105 in collaboration agreements with
  municipalities/provinces. 38 pickups with water tanks. 27 new trucks being acquired.
  20 bulldozer teams (preventive year-round) + 20 more in EPA (high danger). 2+ extra
  water tankers (>25,000L each). 15 PMA vehicles. 15 drones. 322 surveillance cameras.
- **Helibases in Ávila province**: El Barco (ELIF), Piedralaves (ELIF), Cebreros (ELIF),
  Puerto El Pico (BRIF B — MITECO). Rosinos (Zamora) also covers Ávila with 2 ACT.
- **Transition to Tragsa**: 49 of 111 ground teams transferring to state-owned Tragsa,
  gradually, with full conversion by 2029, costing an additional €40M/year (54M→101M
  over the ramp).
- **Current deployment to Burgohondo fire** (Palencia en la Red, 26 July): INFOCAL
  deployed 109 medios total (95 terrestres, 14 aéreos), 560 professionals. Breakdown:
  16 ground teams, 12 helitransported teams, 23 autobombas, 7 bulldozers, plus MITECO
  reinforcement and convoys from Galicia, Madrid, Extremadura, Murcia, Asturias,
  Andalucía, and Portugal. 3,000 total professionals deployed across all three active
  fronts (Diario de León, 28 July).

Sources:
- Junta de Castilla y León, "Medios de lucha" (official):
  https://medioambiente.jcyl.es/web/es/medio-natural/incendios-forestales-medios-lucha.html
- Europa Press, "periodo de riesgo alto" (2026-06-12):
  https://www.europapress.es/castilla-y-leon/noticia-periodo-riesgo-alto-incendios-inicia-hoy-operativo-cyl-5075-profesionales-35-medios-aereos-20260612130848.html
- El Debate (2026-06-13): https://www.eldebate.com/espana/castilla-y-leon/20260613/castilla-leon-prepara-otra-temporada-incendios-5000-profesionales-35-medios-aereos_428216.html
- Servicios Emergencia (2026-02-18): https://serviciosemergencia.es/noticia/4816-castilla-y-leon-refuerza-la-lucha-contra-incendios-forestales-con-27-camiones-autobomba-y-cuatro-cuadrillas-helitransportadas/
- El Día de Valladolid (2026-02-14): https://www.eldiadevalladolid.com/noticia/za519ab82-e907-4129-b01f2d15635f5ac7/202602/cyl-contara-este-ano-con-medio-millar-de-medios-antiincendios
- Infobierzo / Palencia en la Red (2026-01-14):
  https://www.infobierzo.com/castilla-y-leon/castilla-leon-presupuesto-prevencion-incendios-millones-euros_1031681_102.html
- El Norte de Castilla (2026-06-03): https://www.elnortedecastilla.es/castillayleon/operativo-incendios-junta-suma-355-efectivos-partida-20260603195121-nt.html
- La Razón (2025-12-23): https://www.larazon.es/castilla-y-leon/junta-castilla-leon-incorporara-sus-compromisos-operativo-incendios-prorroga-presupuestos-2026_20251223694afbd9ea66eb73531d68af.html
- Diario de Castilla y León (2025-10-14): https://www.diariodecastillayleon.es/castilla-y-leon/251014/102464/lucha-incendios-dispara-gasto-medio-ambiente-presupuestos.html
- El Día de Valladolid (2026-04-22): https://www.eldiadevalladolid.com/noticia/zff9728e5-f2cc-477e-b4b2cbb1e915a485/202604/la-junta-refuerza-con-otros-15m-el-operativo-antiincendios
- Palencia en la Red, despliegue actual (2026-07-26): https://www.palenciaenlared.es/el-operativo-infocal-mantiene-desplegados-109-medios-y-560-profesionales-para-combatir-el-incendio-de-burgohondo/
- Diario de León / ICAL (2026-07-28): https://www.diariodeleon.es/castilla-y-leon/260728/2092524/incendio-avila-sigue-control-3-000-profesionales-tres-frentes.html

### National-level funding context (journalistic findings)

Several investigation pieces from the same week provide the macro context for both regions:

1. **Prevention spend halved (ASEMFO/MITECO data)**:
   - Prevention investment fell 51% from €364M (2009) to €175.8M (2022) — last year with
     consolidated data. Never recovered from the 2011 crash (57% single-year cut).
   - Extinction spend held stable at ~€417M/year over the same period.
   - Prevention's share of total fire budget: 47% (2009) → 30% (2022).
   - Target per Plan Forestal Español 2022-2032: 60/40 prevention/extinction ratio.
     Reality: 12% prevention, 78% extinction per sector analysts.
   - Sources: Gaceta.es (2026-07-28): https://gaceta.es/espana/la-inversion-publica-en-prevencion-de-incendios-forestales-se-ha-reducido-un-50-en-la-ultima-decada-municipios-llevan-12-anos-sin-hacer-un-cortafuegos-20260728-0113/
     La Razón (2026-07-21): https://www.larazon.es/sociedad/espana-destina-78-gasto-apagar-fuegos-solo-12-prevenirlos-ano-doble-bosque-calcinado_202607216a5f1f86f172396e89eb4fb0.html
     El Plural (2026-07-05): https://www.elplural.com/politica/espana/paradoja-incendios-espana-menos-prevencion-mismos-medios-peores-fuegos-historia_394724102
     El Debate (2025-08-16): https://www.eldebate.com/sociedad/sociedad-medio-ambiente/20250816/tijeretazo-sanchez-gasto-incendios-dispara-diez-terreno-arrasado-fuego_326023.html

2. **EU NextGen funds — only 26.4% executed**:
   - €401M allocated specifically for forest management / fire prevention within the
     Component 4 of the PRTR (Plan de Recuperación). As of July 2026, only €105.7M
     formalized/granted (26.4%) per AIReF. ~295M remain unmobilized.
   - Of 310+ planned projects, ~120 have started, ~190 are still pending.
   - CCAA have managed ~58% (€61.6M) of what has been executed; the State directly
     managed only ~€28M.
   - MITECO counters with a broader figure: €1,709M in adaptation measures with
     fire-prevention impact (includes water, ecosystem restoration, etc.).
   - Sources: El Independiente (2026-07-28): https://www.elindependiente.com/espana/2026/07/28/solo-se-ha-ejecutado-el-26-por-ciento-de-los-401-millones-de-euros-de-fondos-europeos-para-luchar-contra-los-incendios/
     Vozpópuli (2026-07-11): https://www.vozpopuli.com/economia/el-caos-administrativo-bloquea-312-millones-de-fondos-para-luchar-contra-los-incendios.html
     OK Diario (2026-07-28): https://okdiario.com/economia/cuentas-publicas/airef-desmonta-propaganda-antiincendios-del-gobierno-solo-gasto-cuarta-parte-fondos-europeos-19082484

3. **State-level PGE (prorogued from 2023) fire budget**:
   - 2026: €98.7M baseline, expanded to €113.37M (+14.69M, +12% vs 2025).
   - Prevention component within this: only ~€11.75M executed by May (10.4% of budget,
     up from 8.2% in 2025).
   - Government claims: +34% extinction spending 2024-2026, +30% prevention spending,
   +47% BRIF budget.
   - Sources: Artículo14 (2026-07-11): https://www.articulo14.es/economia/el-gobierno-solo-ha-destinado-el-10-del-presupuesto-para-la-prevencion-de-incendios-20260711.html
     EFE (2026-07-28): https://efe.com/espana/2026-07-28/gobierno-gasto-extincion-incendios-entre-2024-2026/
     20 Minutos (2026-07-28): https://www.20minutos.es/nacional/gobierno-dice-haber-destinado-130-millones-gestion-forestal-aunque-reitera-que-corresponde-las-ccaa-prevenir-incendios_7019753_0.html

4. **Castilla y León chronic under-execution (journalistic evidence)**:
   - EL PAÍS (2026-06-25) documented: promised helicopter reinforcements not delivered
     to multiple bases at start of season; El Oterico base partially built (no fence,
     no kitchen, donated lockers); El Barco de Ávila helicopter missing at campaign
     start. "Cuadrillas incompletas, falta de helicópteros, camiones parados porque no
     hay conductores." Only ~50% of promised equipment arrived.
   - 12 aeronaves MITECO vs 4 de la Junta in León fires (elDiario.es, 2026-06-25).
   - Source: https://elpais.com/espana/2026-06-25/los-bomberos-de-castilla-y-leon-se-preparan-para-otro-verano-con-falta-de-helicopteros-y-personal.html
     https://elbierzo.eldiario.es/el-bierzo/12-aeronaves-frente-cuatro-gobierno-vuelve-salir-rescate-junta-emergencia-incendios-leon_1_13332526.html

### Updating this dataset

The data found in this pass is structurally different from the earlier rows in `wff_spending.csv`:
- Budget figures from press (Junta's own Cortes testimony, budget-law proposals) represent
  approved/presupuestado amounts, not executed/liquidado — same caveat as C9 for all other
  rows.
- Operational resources (personnel, aircraft, vehicles) are press-relayed from each CCAA's
  own seasonal-device announcements — these are real, but the exact headcounts/counts depend
  on what each CCAA chooses to disclose.
- The national-level findings (EU funds, prevention-spend trend) are not CCAA×year rows —
  they're added to this index as macro context and could feed a separate national-aggregate
  time series in a future T8 expansion.

See also separate report `reports/wff_2026_crisis_response.md` for a consolidated narrative.

### Next step after round 3

Tracing every `confidence=low` row's `source_ref` to a live, re-verifiable URL
(most of round 3's rows were either recovered from a crashed-agent cache or
cited without a captured URL); and T6's few `proyecto`-stage total-budget rows
(Aragón, Cantabria, Castilla y León, Extremadura) should be confirmed against
final Cortes/Asamblea approval once available.

## Round 4 (2026-07-29) — Deepened coverage: Cataluña, Canarias, Baleares, Murcia, Cantabria

Four parallel research agents searched for journalistic/news sources in Spanish
and Catalan for each CCAA. All new sources are documented per-row in
`wff_spending.csv` and `wff_operational_resources.csv`. Key findings:

### Cataluña

Major revision. The 18M€ figure in the previous pass was the **historical**
Pla de Prevenció 2022-2025 (4yr, 72M€ total, 18M€/yr, superseded). Current
spending is substantially larger:

- **387M€** (2026 proposed, program 223, Bombers de la Generalitat — urban + wildfire
  combined, same scope as existing 2020/2021 rows). 2025 actual executed: 367M€.
  2026 proposed was 392M€ but not passed (budget withdrawn Mar 2026, approved Jul 2026).
- **36.8M€/year additional** (new Estratègia Antiincendis, 14 containment axes,
  professionalization, firebreak strips). Total: 131.8M€ by 2033.
- **15M€/year** firebreak strips (subset of 36.8M€, 5yr × 15M€ = 75M€, 10x previous).
- **Academic estimate** (The Conversation 2026-07-27): 327M€ wildfire-specific for
  Catalonia (excluding urban fire), vs 367-387M€ total program 223.
- Pla Bombers 2030: target 4,000 professionals.
- Source key: Cataluña "encara no separa de manera clara la despesa destinada a
  prevenció i la dedicada a extinció" (still does not separate prevention/extinction).

Sources:
- Regió7 / La Ciutat (2026-02-27): Interior budget presentation, 387M€ for program 223
- El Periódico / Empordà (2026-05-05): 367M€ 2025 actual, 392M€ 2026 proposal
- La Vanguardia (2026-05-11) / Europa Press (2026-05-12): 36.8M€ forest strategy
- Crónica Global (2026-07-17): 15M€ firebreak strips (replaces earlier misattribution)
- RTVE Catalunya (2026-06-12): Summer campaign resources
- The Conversation (2026-07-27): Academic cross-CCAA estimate
- Govern.cat (2022): Original 72M€ prevention plan (now superseded)
- Ara.cat (2026-07-10): 131.8M€ containment axes cost by 2033

### Canarias

No single consolidated regional wildfire budget exists — competencies split
across Gobierno de Canarias + 7 cabildos insulares. Best available figures:

- **EIRIF (regional)**: €11.6M/year (€39M/3yr incl. €15M modernization)
- **Tenerife**: €26.5M (Servicio Técnico de Gestión Forestal — prevention+extinction)
- **Gran Canaria**: ~€5M (Céntimo Verde Forestal) + UOFF (undisclosed)
- **Fuerteventura**: €1.28M (fire service — exempt from INFOCA per Decree 180/2025)
- **La Gomera**: €2.5M (annual campaign)
- **Lanzarote**: €9.01M (Consorcio, all emergencies)
- **El Hierro**: €4.27M (4yr TRAGSA contract)
- **La Palma**: €620K (prevention+extinction)

Added EIRIF as closest figure to a regional wildfire budget (`confidence=unverified`,
`coverage=partial` — excludes island-level spending where most competencies sit).
Island-level budgets documented in notes but not added as rows (would sum to
a misleading total across inconsistent scope boundaries).

### Islas Baleares

Confirmed no consolidated wildfire total exists. Money split across two agencies:
- **DGMNGF** (Direcció General de Medi Natural i Gestió Forestal): >60M€ total budget
  (covers all natural environment, not just fires). Fire-specific sub-lines within:
  Gestió Forestal ~9M€, Sanitat Forestal 4.3M€.
- **IBANAT** (Institut Balear de la Natura): ~23M€ total budget (extinction ops +
  prevention + nature conservation). IBANAT brigades form core of extinction response.
- Added IBANAT 23M€ row as closest proxy (`coverage=partial`, `confidence=low`),
  clearly noted as including non-fire costs.

Source: Balears Vadevi (2025-06-08), conseller Simonet Parliament testimony.

### Región de Murcia

Reconciled conflicting figures — they refer to different scope levels/time horizons:
- **28M€** (El Debate): PROJECTED annual average of the 2028-2032 future contract
  (140M€/5yr), NOT the current 2026 budget.
- **~16M€/year** (current 2023-2027 contract: 80M€ total for Servicio de Prevención
  Selvícola y Defensa del Patrimonio Natural). Covers 350 forest firefighters,
  rising to 379 in 2028 (+29 posts, 91% 12-month contracts).
- **21M€ over 20 months**: Additional prevention spending (forest decline treatments).
- **7.2M€/2yr**: Aerial means (1 coordination aircraft + 3 firefighting helicopters +
  1 BRIHELI).
- **450+ daily personnel** (Plan INFOMUR): 19 BRIFOR brigades, 4 BIR, 3 BRIHELI,
  145 daily professional firefighters, ~700 total plantilla including municipal.
- The 14M€ figure from earlier pass was NOT found in any source — possible explanation:
  a narrower scope (e.g., Rural Development ministry's prevention-only budget).

Sources: La Opinión (2026-07-20/27), elDiario.es Murcia (2026-07-20), La Verdad
(2026-07-20), Totana Noticias (2025-09-19), BORM Plan INFOMUR 2026.

### Cantabria

Reconciled conflicting figures — NOT contradictory, different scope levels:
- **26.3M€** (official Govt announcement 2026-01-13): TOTAL cross-government wildfire
  investment (all departments, incl. infrastructure, personnel, ops, equipment).
- **7M€** (Plan Anual de Incendios Forestales 2026, BOC Dec 2025): Narrower — budget
  of the Rural Development ministry's statutory annual plan. 2025 version was 8.4M€.
- **31.5M€** (Presidencia budget): Even broader — total Protección Civil y Emergencias.
- **3.5M€**: Helicopter contract (Maya Dama/Delta Romeo).
- Key finding: second helicopter tender (1M€/3yr, for year-round firefighting) went
  **DESIERTA** June 2026 — no bidders (insufficient budget, rigid specs, no base,
  no cost-of-living adjustment). Cantabria still lacks a year-round dedicated
  firefighting helicopter (Delta Romeo is 365-day but lacks water-bombing cert).

Sources: Gobierno de Cantabria (2026-01-13), Europa Press, elDiario Cantabria,
BOC Plan Anual 2026, Castro Digital (2026-06-25), Europa Press (2026-04-28).

### Operational resources updated

All 5 CCAAs above had their `wff_operational_resources.csv` rows enriched with the
new findings (personnel breakdowns, aircraft counts, vehicle numbers, fleet contracts).
See that file for row-level source citations.

### SPEC.md §T update recommendations

- **T2/T3**: Cataluña, Canarias, Baleares, Murcia, Cantabria all now have improved
  coverage beyond a single sourced figure. Canarias still `coverage=partial` but no
  longer empty. Cataluña coverage markedly deepened (5 rows now). Gap list narrowed
  to: Aragón (still `supera los 54M`, no exact figure), La Rioja (20M vs 9.2M
  unresolved), Navarra (42.7M includes general firefighting).
- **T8**: Cataluña now has 5 sourced years (2020 liquidado, 2021 presupuestado+liquidado,
  2025 liquidado, 2026 presupuestado). Murcia now has 4 rows (current + future contract,
  prevention, aerial means).
- **T10/T11**: EGIF data + operational resources both updated with Canarias, Murcia,
  Cataluña, Cantabria, Baleares enrichments.
