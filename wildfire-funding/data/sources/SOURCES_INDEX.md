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

## Next steps

See `../../SPEC.md` §T (T2–T6): start with the 4 disclosed-split CCAAs
(T2) since they need no estimation, in parallel with the population (T4)
and total-budget (T6) denominators which don't depend on the funding data.
