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

## Next steps

See `../../SPEC.md` §T. **T10** (rerun the now-resumable Tier-1 Hacienda
parser — it crashed on the first full run, output was lost, but the
script now writes incrementally and retries transient errors) is the
next concrete action. After that: tracing every `confidence=low` row's
`source_ref` to a live, re-verifiable URL (most of this round's rows were
either recovered from a crashed-agent cache or cited without a captured
URL); extending Madrid/Aragón/the remaining CCAAs beyond what real search
effort already ruled out this round; and T6's few `proyecto`-stage
total-budget rows (Aragón, Cantabria, Castilla y León, Extremadura)
should be confirmed against final Cortes/Asamblea approval once
available.
