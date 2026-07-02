# T42 — Sexual-crime category & nationality trend analysis

Full results for T42 (`src/plot_sexual_crime_trends.py`). SPEC.md's T42 row
keeps only a summary; this file is the source of record.

Descriptive/correlational only (⊥ causal, V9).

## (a) Per-category time series

Post-V24 collapse (`agresion_sexual_unified`,
`agresion_sexual_con_penetracion_unified` + 8 stable categories) — both
unified series roughly monotonic ↑ 2019→2024 (8.9k→13.7k, 3.1k→5.2k).

## (b) Per-nationality time series

Spanish/foreign perpetrator counts reconstructed from region subtotals +
`foreign_pct` (no direct absolute Spanish count in MIR) — both ↑ but
foreign grew faster (3.4k→5.6k, +65%) than Spanish (6.3k→8.7k, +39%).

Per-country series limited to Marruecos/Argelia/Colombia/Rumanía — the
only 4 country names spelled identically across all 5 report years *and*
with usable `migration_spain.csv` flow coverage; other countries' MIR
spellings vary by year (e.g. CHINA/CHINA POPULAR, PAKISTAN/PAQUISTAN) —
flagged as unresolved name-instability, not normalized.

## (c) Correlations

Descriptive only, n≤5 report years, ⊥ causal per V9:
- total_crimes vs annual inflow: r=0.91
- total_crimes vs migrant-population-share: r=0.97
- per-country crimes vs 3yr-cumulative-inflow: r=0.98-0.99 (MA/DZ/CO/RO)

All strongly positive but on 4-5 points each, not a hypothesis test.

## Output

`data/processed/sexual_crime_evolution.csv` (153 rows) +
`sexual_crime_category_trends.png` + `sexual_crime_nationality_trends.png`
+ `sexual_crime_migration_correlation.png`, all visually verified.
