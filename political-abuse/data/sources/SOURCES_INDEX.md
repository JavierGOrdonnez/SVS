# Sources Index — PPSA

Living index of sources found so far. Nothing here has been cross-checked
against the primary judicial record yet (per `../../SPEC.md` C1/C9) — treat
every case below as `confidence=unverified` until a docket number or
official ruling is located and confirmed.

## Individual cases surfaced by an initial search pass (2026-07)

| Party (at time of position) | Case | Status as reported | Reported by |
|---|---|---|---|
| PSOE | Ex-concejal, Massalfassar (Valencia) — sexual abuse of a co-worker (2018 facts) | Convicted, 4 years prison; expelled from party March 2019 upon being processed | [Público](https://www.publico.es/sociedad/condenado-cuatro-anos-carcel-exconcejal-psoe-abusos-sexuales.html) |
| PP | Carlos Gil, alcalde de Benavites (Valencia) and diputado provincial | Convicted, 10 months, gender violence against his partner | via [sueldospublicos.com](https://www.sueldospublicos.com/texto-diario/mostrar/2617062/sueldos-publicos-cuatro-politicos-condenados-violencia-machista-pp-podemos-vox-psoe) |
| Unidas Podemos | Casiano Antonio Hernández, concejal, Becerril de la Sierra (Madrid) | Detained May 2020, alleged sexual abuse of a minor — reported as investigation stage, **not a confirmed conviction**; needs case-status confirmation | via [sueldospublicos.com](https://www.sueldospublicos.com/texto-diario/mostrar/2617062/sueldos-publicos-cuatro-politicos-condenados-violencia-machista-pp-podemos-vox-psoe) |
| Vox | Carlos Flores, diputado (Congreso) | Convicted 2002 (pre-Vox founding, carried into the party when he later joined/was elected under Vox) — habitual psychological violence; party retained his seat | [Diario Socialista](https://diariosocialista.net/2025/11/10/cuatro-de-los-cinco-condenados-por-violencia-de-genero-en-vox-son-del-pais-valencia/) |
| Vox | "At least 5 elected Vox officials" with sentencia firme for gender violence since 2002, per this source; 4 of 5 in Comunitat Valenciana | Convicted (mixed dates); most cases led to local resignation/removal, one (Flores) retained | [Diario Socialista](https://diariosocialista.net/2025/11/10/cuatro-de-los-cinco-condenados-por-violencia-de-genero-en-vox-son-del-pais-valencia/) |
| Sumar | Íñigo Errejón, ex-portavoz Sumar en el Congreso | Resigned Oct 2024 after public accusations of "violencia machista" + a sexual-harassment complaint — **status as judicial proceeding unconfirmed**, needs to check whether a denuncia was formally filed/admitted | [Público](https://www.publico.es/politica/errejon-denuncias-politicos-violencia-machista-reaccion-social-acarrearon.html) |

**None of the above rows are usable in `ppsa_cases.csv` yet** — each needs
(a) the actual court/case reference per C1, and (b) a confirmed
`case_status` per C2, since news summaries conflate "denunciado",
"detenido", "procesado" and "condenado" loosely.

## Secondary/overview coverage (context, not yet case-level sourced)

- [Los sueldos públicos de cuatro políticos condenados por violencia machista: PP, Podemos, Vox y PSOE](https://www.sueldospublicos.com/texto-diario/mostrar/2617062/sueldos-publicos-cuatro-politicos-condenados-violencia-machista-pp-podemos-vox-psoe) — one case per party, useful starting index, not a comprehensive registry.
- [Los escándalos sexuales cercan a la izquierda política española (Moncloa.com, 2025-12-11)](https://www.moncloa.com/2025/12/11/escandalos-izquierda-politica-3346345/) — overview piece, left-leaning parties; cross-check claims individually, this is an opinion/analysis outlet not a court record.
- [Más allá de Errejón: otras denuncias a políticos por violencia machista (Público)](https://www.publico.es/politica/errejon-denuncias-politicos-violencia-machista-reaccion-social-acarrearon.html) — lists several additional named cases across parties; needs case-by-case follow-up.

## Denominator sources (C4)

- Ministerio del Interior — historical election results (elected officials
  by party, by election, going back decades): `https://www.infoelectoral.mir.es/` —
  gives elected-office headcounts (concejales, diputados autonómicos/nacionales,
  senadores) per party per election cycle. Does **not** cover appointed
  posts or party staff.
- No centralized registry found (yet) for altos cargos / personal
  eventual / party-employed staff by party — see SPEC.md R2. Candidates to
  chase: Portal de Transparencia (state + each CCAA's own), Tribunal de
  Cuentas party-finance filings (list some paid staff), direct FOI
  requests to party headquarters (tuderechoasaber.es is a working Spanish
  FOI-request platform used successfully for adjacent questions, e.g. a
  request titled "Número de cargos políticos empleados por la
  Administración Pública" — see that platform for a template on how such
  requests are worded/routed).

## Judicial aggregate statistics checked (not usable as a shortcut)

- CGPJ / Poder Judicial — [Estadística Judicial, Violencia doméstica y de
  género](https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estadistica-por-temas/Datos-penales--civiles-y-laborales/Violencia-domestica-y-Violencia-de-genero/) —
  publishes convicted-person breakdowns by age/sex/nationality, **not** by
  profession or political affiliation (confirmed by initial search, SPEC.md
  R3). Useful only as national base-rate context, never as a per-party
  source.

## Next steps

See `../../SPEC.md` §T (T2–T5): confirm each case above against a real
court reference before it enters `ppsa_cases.csv`, and start T4 (elected
headcount build from infoelectoral.mir.es) in parallel since it does not
depend on case sourcing.
