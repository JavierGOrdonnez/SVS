# SPEC.md — WFF (Wildfire Prevention & Extinction Funding, Spain)

Entry point for anyone (human or agent) working in `wildfire-funding/`.
Structured after SVS's `../SPEC.md` (§G/§C/§R/§I/§V/§T sections) for
consistency; this project's data, invariants, and roadmap are entirely
separate from SVS's violence-probability model.

---

## §G — Goal

Per Spanish autonomous community (CCAA) and year: how much public money is
spent on wildfire prevention and on extinction (separately where
disclosed, flagged undisclosed where not), and how does that compare across
regions once normalized by (1) population, (2) forest area, (3) the
region's own total budget. Secondary goal: build the longest sourceable
year-over-year series per CCAA to test whether prevention funding actually
drops once a severe fire season ends.

---

## §C — Constraints

C1: ∀ figure → cite the exact source: official budget law (Ley de
Presupuestos) article/annex, or the specific report/table if from a
secondary compiler (Greenpeace, ASEMFO, a fact-checker), plus year of
publication. Never cite a news article's number without checking whether
it itself cites an identifiable primary source.

C2: **Category split ⊥ inferred.** `prevención`, `extinción`, and
`no desglosado` are three distinct, mutually exclusive values for a
spending row's `category` field. If a CCAA's budget document only gives a
combined figure, the row goes in `no desglosado` — it is never split
proportionally or estimated to force it into the other two buckets.
*(Deprioritized 2026-07-27: getting all 17 CCAAs covered with at least one
sourced total took priority over chasing the prevention/extinction split
for the handful of regions that disclose it — see T2/T3. The constraint
itself still holds if/when that split is added back: no inferred numbers,
ever.)*

C3: **Nominal vs. real euros.** Any multi-year comparison must state
whether figures are nominal or inflation-adjusted (INE IPC series), and
must not mix the two within one chart/table. Default to nominal in the raw
dataset; compute real-terms series as a clearly labeled derived column.

C4: **Population denominator** = INE population by CCAA for the same year
as the spending figure (Padrón through 2020, Estadística Continua de
Población / Censo Anual de Población from 2021 onward per the INE
methodology break — document which series a given year uses).

C5: **Forest-area denominator** = Cuarto Inventario Forestal Nacional
(IFN4) per-CCAA forest surface, or MITECO's more frequently updated Mapa
Forestal de España where available. IFN4 fieldwork was conducted at
different times per CCAA (roughly 2005–2015ish, not simultaneous) — this
non-simultaneity must be documented, not silently treated as one snapshot
year for all regions.

C6: **Total CCAA budget denominator** = the "presupuesto inicial" (initial
approved budget) figure from the Ministerio de Hacienda's official CCAA
budgets portal (`serviciostelematicosext.hacienda.gob.es`) for the matching
year, unless a row explicitly notes it's using executed spend instead —
the two must never be silently mixed. **First pass (2026-07-27)**: populated
via regional press coverage of each budget law's passage instead (Hacienda's
own portal is a JS-driven query tool WebFetch can't drive), each row tagged
`aprobado_definitivo` / `proyecto` / `proyecto_convalidado` per how far the
law had actually progressed at time of sourcing — see `wff_denominators.csv`.
Revisit against Hacienda's own consolidated table when feasible.

C9: **Budgeted ≠ executed, and executed is the number that matters.**
Every `wff_spending.csv` figure sourced so far is an *initial credit or
announced device budget* (crédito inicial), not audited final expenditure
(liquidación). Wildfire spending is exactly the kind of item that
routinely blows past its initial credit via extraordinary in-year credits
once a season turns out worse than planned — nominal series (T8) that
only track the announced figure will understate real cost in bad years
and can't be compared across CCAAs that differ in how often they need
supplementary credits. A `spend_type` value of `presupuestado` vs.
`liquidado` is required once liquidación data is sourced (each region's
Intervención General / Cuenta General, published with a 1-2 year lag);
until then every row is implicitly `presupuestado` and must not be
described as "what was spent."

C7: A CCAA that extends its previous year's budget (no new law passed —
this happened e.g. Cataluña for 2024 per initial research) must have that
noted explicitly on the affected row rather than treated as a fresh
same-year figure.

C8: All confidence-tagging conventions from `../SPEC.md` C1/C12 (source
citation, `confidence` field, `unverified` rows excluded from any public
figure) apply here unchanged.

---

## §R — Research (open questions, not yet resolved)

R1: Best per-CCAA, per-year, prevention-vs-extinction-split source.
Leads found so far (see `data/sources/SOURCES_INDEX.md`): ASEMFO's
"Estudio de Inversión en el Medio Forestal" series (2005–2022, XIII
edition found), Greenpeace's "Grandes incendios forestales" annual report
(explicitly tracks the disclosure gap), MITECO/EGIF preliminary and
definitive fire statistics (fire counts/area, not funding). None of these
alone covers all 17 CCAAs with a clean prevention/extinction split for all
years — expect to combine several and document per-CCAA-per-year source
provenance individually.

R2: **Resolved (first pass)** — used MITECO's *Anuario de Estadística
Forestal 2019*, table 6.1.1 ("Superficie arbolada, desarbolado y
forestal, MFE25-MFE50, 2019"), which already tabulates total forest
surface for all 17 CCAAs from the Mapa Forestal de España in one document
— simpler than assembling 17 separate per-region IFN4 editions with
non-simultaneous fieldwork years. Trade-off accepted: single 2019
snapshot for all regions, not each region's own most-current figure.
Revisit if a more recent MITECO Mapa Forestal update consolidates all
CCAAs the same way.

R3: Whether "presupuesto inicial" (approved) or actual executed spend is
more meaningful for the prevention-funding-drops-after-fires hypothesis —
approved budgets can be revised upward mid-year after a bad season
(modificaciones presupuestarias, tracked by Newtral's tracker per initial
search) — decide once R1's data granularity is known.

---

## §I — Interfaces

```
file: data/raw/wff_spending.csv          → one row per (ccaa, year, category, amount_eur, source) — schema TBD in T1
file: data/raw/wff_denominators.csv      → one row per (ccaa, year, population, forest_area_km2, total_budget_eur) — schema TBD in T1
file: data/sources/SOURCES_INDEX.md      → living index of sources consulted, incl. R1/R2/R3 findings
```

---

## §V — Invariants

V1: ∀ row in `wff_spending.csv` → `ccaa`, `year`, `amount_eur`,
`spend_type` ∈ {presupuestado, liquidado}, `source_name`, `confidence` —
all non-empty. `program_code`/`program_name` (the region's own official
budget-line label, free text — no shared taxonomy forced across CCAAs) are
required once a row is sourced from an official presupuesto-por-programas
or ejecución-presupuestaria document (T9/T10), optional for the earlier
press-relayed rows. `category` ∈ {prevención, extinción, no_desglosado}
is aspirational per C2 but not currently a populated column — see T1's
2026-07-27 note.

V2: ∀ row in `wff_denominators.csv` → `ccaa`, `year`, `population`,
`population_source_series` (Padrón vs. ECP/Censo per C4), `forest_area_km2`,
`forest_area_source_year` (per C5's non-simultaneity note),
`total_budget_eur`, `budget_type` (inicial vs. ejecutado per C6) — all
non-empty.

V3: A normalized figure (€/100k hab, €/km², % of total budget) is never
published without also showing the raw `amount_eur` and the exact
denominator value+source used — normalization ratios alone invite
misreading small regions as extreme outliers or vice versa.

V4: `no_desglosado` rows ⊥ silently excluded from any "total spend"
figure — a region's total (prevention + extinction + undisclosed) must
still reconcile to its own reported combined total where one exists.

---

## §T — Tasks

| id | status | track | what/where |
|---|---|---|---|
| T1 | x | infra | `data/raw/wff_spending.csv` / `wff_denominators.csv` schemas built and populated (first pass). Category split (C2) deprioritized per explicit user direction 2026-07-27 — "coverage of all regions is more important" than the prevention/extinction breakdown; `wff_spending.csv` currently carries one `amount_eur` per CCAA×year rather than the three-way category split, with per-row `notes` documenting known scope conflicts instead. |
| T2/T3 | ~ | data | 16 of 17 CCAAs now have ≥1 sourced spend figure for 2025/2026 (Canarias excluded — no consolidated regional total exists, competencies split across cabildos insulares, documented in `SOURCES_INDEX.md`). Every populated row is `confidence=low` or `medium` and most carry an unresolved conflicting alternate figure from a second source (see `notes` column) — none of this is ready to publish as a definitive ranking without T2-style primary-source tracing per region. |
| T4 | x | data | Population denominator built for all 17 CCAAs, INE Censo Anual de Población 2024 (via es.wikipedia.org secondary relay of INE figures — not fetched from INE's own interactive table directly, since that requires JS-driven parameter selection WebFetch couldn't drive; revisit with a direct INE CSV export if precision matters). |
| T5 | x | research/data | R2 resolved — forest-area denominator built for all 17 CCAAs from MITECO's Anuario de Estadística Forestal 2019, table 6.1.1 (a real primary source, extracted via pdfplumber from the actual PDF, not a secondary relay). |
| T6 | ~ | data | Total-CCAA-budget (initial/approved) sourced for 15 of 16 spend-covered CCAAs via regional press coverage of each 2025/2026 budget law (see C6, `wff_denominators.csv`); several still `proyecto`/not-yet-Cortes-confirmed at time of sourcing (Aragón, Cantabria, Castilla y León, Extremadura). Executed/liquidación figures — the ones that actually matter per C9 — not started; that's a separate, harder pull (each region's Intervención General, 1-2yr lag). |
| T7 | x | analysis | `analysis/compute_normalized.py` joins spending × denominators and writes `reports/wff_first_pass_2025_2026.md` — € /100k hab, € /km² forest, and % of own budget (where spend-year and budget-year are within 1 year) computed for the 16 covered CCAAs. Ranking already visibly reshuffles under each normalization vs. raw totals, as the project's motivation predicted. |
| T8 | ~ | analysis | Historical time series deepened: Galicia/PLADIGA now has 6 sourced years (2019-2021, 2023-2025, all partial investment-line slices), Andalucía/Plan INFOCA has 5 (2020-2024, 2026), Castilla-La Mancha/Plan INFOCAM has 2 (2025-2026). Everything else is still a single year (Aragón, Madrid: no second year found this pass despite real search effort — documented gap, not filled). National aggregate lead (`forescat.com`/ASEMFO, 2000–2024) still untraced. |
| T9 | ~ | data | Executed vs. budgeted (C9) — schema extended and populated. 5 real presupuestado/liquidado pairs now computable (see `reports/wff_first_pass_2025_2026.md`'s Execution rate table): Castilla y León 2025 (48.5%, mid-year snapshot pre-fire-season), Cataluña 2021 (106.6%, broader-than-wildfire scope), Extremadura 2024 (2 pairs: 40.8% aggregate, 8.9% on the narrowest project line), País Vasco/Bizkaia 2023 (0€ initial credit → 1.34M executed via in-year credit, the clearest example of C9's core concern). All rows `confidence=low`, most pending `source_ref` re-verification (recovered from a crashed-agent research cache, or fetched fresh this pass) — see SOURCES_INDEX.md. Aragón: real search effort made (Cámara de Cuentas, Cortes written answers), no presupuestado/liquidado pair found — documented as a gap. Madrid: intensified round-2 dig (fetched the official structured budget-by-program XLSX directly, all ~100 programs) found the *reason* no pair exists — Madrid's budget structurally does not isolate wildfire spending into its own program (see SOURCES_INDEX.md); added the closest-scope context row (456A Biodiversidad, 51.4M 2026) instead. |
| T10 | x | infra/data | Tier-1 official all-CCAA total-budget parser (`parsers/parse_hacienda_totals.py`) — complete. Made resumable (writes incrementally, retries transient errors) after two mid-run crashes; full sweep now done: `data/raw/wff_total_budget_timeseries.csv` has both `presupuestado` and `liquidado` totals for all 17 CCAAs, 2013-2024. |
| T11 | x | data | Operational-resource capacity: `data/raw/wff_operational_resources.csv` (13/17 CCAAs, 2026, press-sourced, low confidence) **plus** `data/raw/wff_egif_incidents_by_ccaa_year.csv` — 921 CCAA×year rows, 1968-2023, aggregated from Civio's EGIF-derived per-fire dataset (real, downloaded, no registration needed — see `data/sources/private_contractors_and_operations.md`). Includes real extinction-cost (`gastos`) totals for the subset of CCAAs that still report that field: Galicia, Andalucía, Aragón, La Rioja (recent years) — a genuinely important finding in its own right is that most other CCAAs *stopped* reporting extinction costs to EGIF years-to-decades ago (Madrid: 1991), independently corroborating the transparency-decline pattern found in Madrid's case with hard national data. `personal`/`medios` unit definitions not yet confirmed — do not treat as comparable to `wff_operational_resources.csv`'s headcounts without checking. |
| T12 | ~ | research | Private-contractor landscape — see `data/sources/private_contractors_and_operations.md`. Two primary/near-primary findings: (1) Madrid's TRAGSA entrustment document (€107M, 2022-2025) pinpoints the exact budget line (134A/subconcepto 22706) the earlier "Madrid doesn't isolate wildfire spending" finding (T9) had missed. (2) A public-procurement route confirmed accessible (PLACSP bulk XML, no auth; TED search, no auth) with one concrete contract found (Avincis/Andalucía, €319.2M, 2026-2031 per TED — conflicts with the Junta's own €112M authorization figure, unreconciled). Everything else in that file (Cartel del Fuego, CNMC investigation, Castilla y León's ~20-company privatization) remains `confidence=low`/unverified, flagged as needing re-verification before citing as fact. |
