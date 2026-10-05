---
name: demographics-parsers
description: |
  Reference for the 4 demographic-denominator parsers: INE population
  estimates (`src/analysis/parse_ine_population.py`, table 56934), INE
  population by nationality (`src/analysis/parse_ine_population_nationality.py`,
  table 56936), INE mortality by cause/age/sex (`src/mortality/parse_ine_mortality.py`,
  table 7947), and Eurostat per-nationality migration flow/stock
  (`src/migration/parse_eurostat_migration_cohort.py`, migr_imm1ctz/migr_pop1ctz).
  Covers each parser's input format, CLI, output schema, and known
  quirks/gotchas so an agent doesn't have to re-derive them by reading the
  source. Triggers when working on population denominators, age pyramids,
  mortality rates, Spanish-vs-foreign nationality splits, or per-nationality
  migration cohorts — i.e. any task needing a rate *denominator* rather than
  an event count. Replaces SIA-105/106/107/108. Does not cover crime-event
  numerators (see crime-parsers skill) or MIR/sexual-crime/feminicide report
  parsers (see mir-report-parsers skill).
---

# demographics-parsers — population/mortality/migration denominator reference

Four scripts, each targeting a different source format and delivery
mechanism (confirmed **not duplicative** — see `SPEC.md` §R1). None of them
fetch live over HTTP; all take a pre-downloaded input file as a CLI argument
(`curl` first, then run the script) — unlike the crime parsers, which fetch
inline.

## `parse_ine_population.py` — INE table 56934 (population estimates)

- **Input**: pre-downloaded CSV, `https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/56934.csv?nocab=1`. Semicolon-delimited. 109 single-year ages (0–99, 100, "100 y más", plus "Todas las edades") × sex × quarterly reference date (Jan/Apr/Jul/Oct 1), 1971–2025 (some quarters suppressed pre-2002 with `..`).
- **CLI**: `uv run python src/analysis/parse_ine_population.py <in.csv>` (one positional arg, `sys.argv[1]`).
- **Output**:
  - `data/processed/population_spain_estimates.csv` — full long form, one row per (year, ref_date, sex, age_label, population).
  - `data/processed/population_spain_midyear_5yr.csv` — July 1 only, binned into 5-yr age groups (`<1`, `1-4`, `5-9`, …, `90-94`, `95+`) matching the mortality table's bins — this is the rate denominator consumed by `compute_mortality_rates.py`.
- **Quirks**:
  - Only July 1 rows feed the 5-yr-binned output; the other 3 quarters only appear in the long-form CSV.
  - Number format is mixed: Spanish thousands-dot in some rows, plain int in others (post-2021 Censo rows) — `parse_value()` handles both, strips `,` decimals and `.` thousands unconditionally.
  - `95+` bin excludes the raw `"100 años"` label specifically to avoid double-counting against `"100 y más años"` (the real open-ended top group) — both labels exist in the source.

## `parse_ine_population_nationality.py` — INE table 56936 (Spanish/foreign split)

- **Input**: pre-downloaded CSV, `https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/56936.csv?nocab=1`. Same ECP family/cadence as 56934 (quarterly, July-1 midyear reference), but reports `Española`/`Extranjera`/`Total` nationality directly plus individual country/region rows (the latter are read but discarded — this parser only keeps the 3 aggregate labels).
- **CLI**: `uv run python src/analysis/parse_ine_population_nationality.py <in.csv> [out.csv]` (positional; `out.csv` defaults to `data/processed/population_spain_nationality.csv`). Reuses `parse_ine_population.py`'s `SEX_MAP`/`PERIOD_MONTH`/`parse_value`/`parse_periodo`.
- **Output**: `data/processed/population_spain_nationality.csv` — July 1 only, 2002–2025, one row per (year, sex, age_group, nationality, population_july1). `age_group` is `all` or one of the 17 pyramid bands (`0-4`…`75-79`, `80+`); the raw `80-84`/`85-89`/`90 y más años` source bands are summed into `80+`.
- **Quirks**:
  - **Hard floor at 2002** (`MIN_YEAR`) — table 56936's real data floor; do not back-fill earlier years by subtraction (see next bullet).
  - Exists specifically to fix B44: every prior consumer of "Spanish population" in this repo derived it as `total (t.56934) − foreign stock (Eurostat migr_pop1ctz)`, which mixes a July-1 total against a January-1 foreign figure covering only ~86–94% of foreign residents (top ~50 nationalities). This script reports INE's own directly-published `Española` figure — no subtraction, no coverage gap. Don't reintroduce the subtraction method for new code touching Spanish-national population.

## `parse_ine_mortality.py` — INE table 7947 (mortality by cause/age/sex)

- **Input**: pre-downloaded JSON dump from the INE `wstempus` API: `https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/7947?nult=N&tip=A` (fetch via `curl`, not a Python HTTP call inside the script). ~24 MB for 25 years of history, 7,920 series.
- **CLI**: `uv run python src/mortality/parse_ine_mortality.py <in.json> <out.csv>` (two positional args — unlike the two population scripts, output path is also an explicit arg here, not a module constant).
- **Output**: CSV (path given by caller, conventionally `data/processed/mortality_spain_ine_ecm.csv`) — columns `year, sex, age_group, cause_chapter, cause, deaths, data_type, series_cod`.
- **Quirks**:
  - Each series' `Nombre` field encodes sex + age + cause in **two inconsistent string formats** depending on the series (`"{cause}. {sex}. {age}. Total Nacional. Personas."` vs `"{sex}. {age}. Total Nacional. {cause}. Personas."`) — `parse_name()` identifies sex/age by matching fixed vocabularies and treats whatever's left as the cause string; it does not assume field order.
  - Series whose name doesn't match either format (sex/age not found, or no leftover cause text) are silently skipped and counted — check the printed `series parsed: X/Y (skipped Z)` line, not just exit code.
  - `cause` is further split into `cause_chapter` (Roman-numeral prefix, e.g. `"II"` or `"II-IV"`) + bare `cause` text via regex; chapter is `""` when the cause string has no Roman-numeral prefix.
  - Always follow with `summarize_mortality.py <out.csv>` to produce the derived summary CSVs (`mortality_by_chapter.csv`, `mortality_key_causes.csv`, `mortality_by_age_sex.csv`) — this parser only flattens, it doesn't aggregate. Rate computation (`compute_mortality_rates.py`) needs **both** this output and `parse_ine_population.py`'s 5-yr binned output as separate positional args.

## `parse_eurostat_migration_cohort.py` — Eurostat per-nationality migration flow/stock

- **Input**: two pre-downloaded **JSONL** files (one JSON object per line, already decoded from Eurostat's SDMX-JSON API — not the raw bulk TSV), covering immigration flow (`migr_imm1ctz`) and population stock (`migr_pop1ctz`) for a hardcoded `CITIZENS` allowlist (currently ~50 country codes, ~94% of 2025 foreign stock by share, plus `ES` for the Spanish-national denominator used by feminicide rates). Flow coverage 1998–2024, stock 2002–2025.
- **CLI**: `uv run python src/migration/parse_eurostat_migration_cohort.py <flow.jsonl> <stock.jsonl>` (two positional args, no flags).
- **Output**: **appends** to the shared `data/raw/migration_spain.csv` (not a dedicated output file) — two series, `flow_immigration_from_abroad` and `stock_nationality`, each row keyed by (year, sex, age_group, origin nationality code).
- **Quirks**:
  - **Idempotent by full regeneration, not merge**: every run drops ALL existing `source_name == "Eurostat"` rows (plus legacy `stock_foreign_nationality` rows for any nationality now in `CITIZENS`) before appending fresh ones — re-running with an unchanged `CITIZENS` list and unchanged JSONL is a no-op in content but still rewrites the whole file (new `row_id` sequence).
  - `CITIZENS` is a **hardcoded module-level list** — adding a nationality means editing the source and re-running with freshly pulled JSONL for that country; there's no CLI flag for scope.
  - Age bands are a mix of 5-yr bins (`5-9`…`80-84`) and aggregate bands (`Y_LT15`→`0-14`, `Y_LT5`→`0-4`, `Y_GE65`→`65+`, `Y_GE85`→`85+`) — `_age_to_group()` returns `None` (silently dropped) for any Eurostat age code not in this explicit mapping, so a newly-appearing Eurostat age code needs a code change, not just a data re-pull.
  - Known coverage gaps are data-source gaps, not bugs: Austria (AT) was never downloaded; Romania (RO) has gone missing from the CSV before due to a stale regeneration relative to an already-updated JSONL (see `SPEC-migration.md` B36) — if a nationality looks absent, check whether its JSONL actually has rows before assuming a parser bug.
  - `ES` (Spanish nationals) rows from this script **replace** the INE-derived subtraction method for the Spanish-national denominator in some downstream consumers, but the INE `nationality=foreign` aggregate row (from the older subtraction method) is deliberately preserved during the drop/regenerate step — don't delete it as "redundant" without checking which downstream script still reads it.

## Shared conventions across all 4

- None fetch live over HTTP from inside the script — all take pre-fetched input file(s) as positional CLI args (`curl`/manual download happens first, documented per-source in `data/sources/*.md`).
- `parse_ine_population.py` and `parse_ine_population_nationality.py` share `SEX_MAP`, `PERIOD_MONTH`, `parse_value()`, `parse_periodo()` — if you need to change period-string parsing or Spanish number handling, both scripts are affected.
- Confirmed non-duplicative despite surface similarity (semicolon CSV / JSON) — see `SPEC.md` §R1 for the full source/fetch/format/output comparison table across these and the crime parsers.
