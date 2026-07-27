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
the two must never be silently mixed.

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

V1: ∀ row in `wff_spending.csv` → `ccaa`, `year`, `category` ∈
{prevención, extinción, no_desglosado}, `amount_eur`, `nominal_or_real`,
`source_name`, `source_ref`, `confidence` — all non-empty.

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
| T6 | . | data | Total-CCAA-budget denominator — not started. `wff_denominators.csv` has the column but every row is blank; Hacienda's portal URL is documented in `SOURCES_INDEX.md` as the source to use. |
| T7 | x | analysis | `analysis/compute_normalized.py` joins spending × denominators and writes `reports/wff_first_pass_2025_2026.md` — € /100k hab and € /km² forest computed for the 16 covered CCAAs; % of own budget not yet computable (blocked on T6). Ranking already visibly reshuffles under normalization vs. raw totals, as the project's motivation predicted. |
| T8 | . | analysis | Historical time series — not started. National aggregate lead (`forescat.com`/ASEMFO, 2000–2024) still needs tracing to build a real per-CCAA multi-year series. |
