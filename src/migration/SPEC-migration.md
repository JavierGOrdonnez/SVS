# SPEC-migration.md — migration module

Part of the SVS spec. Top-level goal/shared constraints/invariants/roadmap/bug
log live in [`SPEC.md`](../../SPEC.md); this file owns §T tasks T11,
T-mig-tab, T43, T44 and this module's domain-specific §V/§I content only.

---

## §I — Interfaces (migration-specific)

```
file: data/raw/migration_spain.csv                     → migration flows & stock 2000-2025: by sex, age, origin nationality, foreign/Spanish split (T11, 2337 rows; merged from claude/spain-migration-data-PsIYr 2026-06-07); joint age(5yr)×sex×citizenship cross for Morocco/Algeria (flow 1998-2024, stock 2002-2025) added via `src/migration/parse_eurostat_migration_cohort.py` from Eurostat bulk `migr_imm1ctz`/`migr_pop1ctz` (V25 cohort denominator, real data not extrapolated)
file: data/sources/migracion_espana.md                 → migration source doc — INE EMCR/EVR/Padrón/ECP, Eurostat, MISSM table refs + caveats (2008, 2021 method breaks)
cmd:  `uv run python src/migration/parse_eurostat_migration_cohort.py` → Eurostat bulk `migr_imm1ctz`/`migr_pop1ctz` TSV (manual download, not in `data/raw/`) → appends to `migration_spain.csv` (T11,T43,T44)
file: `src/migration/build_dashboard_data.py` (formerly `build_migration_dashboard_data.py`) → `build()` reads `migration_spain.csv`, consumed by `src/analysis/build_dashboard.py` → `docs/data/migration.json` (T-mig-tab)
```

## §V — Invariants (migration-specific)

V25: recent-arrival-cohort population (no direct tenure-stratified table exists) ! approximated as cumulative net migration inflow over the trailing ~3yr window, joined against `migration_spain.csv` (T11) age-band × sex × origin-nationality data (closest available band to 15-59 male); settled_pop = stock − cohort_pop; ⊥ presented without documenting the approximation + its caveats (naturalization, re-emigration, irregular-migration undercount all bias in either direction). UPDATE 2026-07-01: for Morocco (MA) and Algeria (DZ) specifically, `migration_spain.csv` now carries the *real* joint 5yr-age-band × sex × citizenship cross (flow 1998-2024, stock 2002-2025, via Eurostat `migr_imm1ctz`/`migr_pop1ctz` bulk — INE's own tables 24290/36825 only reach 2021/2022) — no extrapolation needed for T41's cohort_pop/settled_pop split for these two countries; the cumulative-inflow approximation above still applies wherever this direct cross is absent (other nationalities in T42's broader correlation scope).

## §T — Tasks (migration)

| id | status | track | task | cites |
|---|---|---|---|---|
| T11 | ~ | C,infra | Populate `data/raw/migration_spain.csv` (2337 rows) — flows 2000-2024, foreign-nationality stock 2000-2025, top-10 origin nationalities for 2008-2024 intake & 2025 stock (sex-split sums match published totals exactly 2008-2024), broad age bands 2008-2024 + granular 5-yr bands 2024, SS-affiliation snapshots; EXTENDED 2026-07-01: joint age(5yr)×sex×citizenship cross for Morocco/Algeria (flow 1998-2024, stock 2002-2025) via `src/migration/parse_eurostat_migration_cohort.py` (Eurostat `migr_imm1ctz`/`migr_pop1ctz` bulk, cross-validated exact match against pre-existing MA totals 2022-2024). See `data/sources/migracion_espana.md` | V10,C8,V25 |
| T-mig-tab | x | infra | Rebuild migration dashboard tab on current `docs/index.html` architecture (T17/T23 tabbed architecture) — charts G1 (inflow + 2008 break), G2 (origin composition), G3 (sex split), G4/G5 (age composition/profile), G6 (stock); delivered via `src/migration/build_dashboard_data.py` (commit `55cfa64`). | I.*,V1,V6 |
| T43 | . | D | Obtain real age×sex×citizenship joint-cross migration/stock data — South America. Extend `src/migration/parse_eurostat_migration_cohort.py`'s `CITIZENS` list beyond `["MA","DZ"]` to add CO, EC, PE, VE, BO, PY, AR (Colombia, Ecuador, Peru, Venezuela, Bolivia, Paraguay, Argentina — the T41 South America group; MIR name-instability caveats from T42 apply when mapping names→codes); re-run against the Eurostat migr_imm1ctz/migr_pop1ctz bulk TSVs (must be manually downloaded — not present in `data/raw/`) to get the real 5yr-age-band × sex × citizenship joint cross per country; append to `migration_spain.csv`. Blocked until the bulk TSVs are obtained. ⊥ approximate the population time series from a single-year snapshot (rejected as not defensible, see crime's T41 report). | V6,V25,C10 |
| T44 | . | D | Obtain real age×sex×citizenship joint-cross migration/stock data — EU-Europe excl. Spain. Extend `src/migration/parse_eurostat_migration_cohort.py`'s `CITIZENS` list to add RO, IT, DE, FR, BG, PT, PL, BE, NL (Rumania, Italia, Alemania, Francia, Bulgaria, Portugal, Polonia, Belgica, Holanda — the T41 EU-Europe group); same Eurostat bulk-TSV source/process as T43 (can be run together in one script invocation once files are downloaded); append to `migration_spain.csv`. Blocked until the bulk TSVs are obtained. ⊥ approximate the population time series from a single-year snapshot. | V6,V25,C10 |

## Related bugs

None specific to this module — see `SPEC.md` §B for the full centralized log.
