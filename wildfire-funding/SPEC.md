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

R2: Whether IFN4 (potentially outdated, fieldwork up to ~20 years old for
some regions) or MITECO's more current Mapa Forestal / Corine Land Cover
derivative is the better forest-area denominator — investigate which is
more consistently available per-CCAA before committing to one.

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
| T1 | . | infra | Design `wff_spending.csv` / `wff_denominators.csv` schemas satisfying V1/V2. |
| T2 | . | data | Source the 4 CCAAs with disclosed prevention/extinction splits (Galicia, Extremadura, Castilla-La Mancha, Baleares) for the most recent available year as the first populated rows. |
| T3 | . | data | Source `no_desglosado` combined totals for the remaining CCAAs, most recent year (2025/2026 budget-cycle figures already surfaced for Comunidad Valenciana, Andalucía/INFOCA, Castilla y León, Galicia/PLADIGA, Extremadura/INFOEX, Asturias, Aragón/INFOAR, Madrid/INFOMA — see SOURCES_INDEX.md). |
| T4 | . | data | Build the population denominator table (INE, per C4) for the same year set as T2/T3. |
| T5 | . | research | Resolve R2 (IFN4 vs. Mapa Forestal) and build the forest-area denominator table. |
| T6 | . | data | Build the total-CCAA-budget denominator table from Hacienda's official portal (per C6), same year set. |
| T7 | . | analysis | Once T2–T6 land for ≥1 year, compute all three normalizations (Table B) and publish the first cross-CCAA comparison, explicitly flagging the `no_desglosado` majority per the transparency caveat in `README.md`. |
| T8 | . | analysis | Extend backward year-by-year (national aggregate already has a 2000–2024 lead via `forescat.com`/ASEMFO — see SOURCES_INDEX.md) to test the funding-drops-after-severe-seasons hypothesis with a real time series. |
