---
name: crime-parsers
description: |
  Reference for the 4 crime-statistics parsers under `src/crime/parse_*.py`:
  INE table 28716 (convictions by crime type × nationality), INE table 28857
  (convictions by sex × age × nationality), the MIR Anuario general-crime PDF
  extraction, and the SES portal hate-crime nationality megatablas. Covers
  each parser's input format, CLI, output schema, and known quirks/gotchas so
  an agent doesn't have to re-derive them by reading the source. Triggers
  when working on crime-nationality data, peligrosity, hate-crime nationality
  breakdowns, the Anuario "Seguridad Ciudadana" tables, or any task citing
  SPEC-crime.md §I rows for these four scripts (T26, T30, T76, T77, T84).
  Replaces SIA-101/102/103/104. Does not cover the MIR Informe/Balance
  report parsers (`src/parsers/*`) or demographic-denominator parsers
  (population/mortality/migration) — those are separate domain skills.
---

# crime-parsers — INE/SES crime-nationality parser reference

Four independent, argument-less scripts (`uv run python src/crime/<script>.py`,
no CLI flags on any of them — each hardcodes its own source/output paths as
module-level constants). Three fetch live over HTTP; one reads local PDFs
already checked into `data/sources/`.

## `parse_ine_tabla28716.py` — convictions by crime type × nationality

- **Input**: live fetch, `https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/28716.csv?nocab=1`. Semicolon-delimited, Spanish number format (`.` thousands, `,` decimal). Coverage 2017–2024.
- **CLI**: `uv run python src/crime/parse_ine_tabla28716.py`
- **Output**:
  - `data/processed/ine_condenados_28716_sexual_crimes.csv` — one row per (year, crime_label, nationality_label, count), Chapter 8 "Contra la libertad e indemnidad sexuales" only.
  - `data/processed/ine_condenados_28716_nationality_pct.csv` — derived `pct_of_total` per (year, nationality_group), EU/non-EU Europe continent groups consolidated.
- **Quirks**:
  - Filters to chapter 8 rows via `nivel2.startswith("8")`; crime label is taken from the finest non-null level (`nivel4` > `nivel3` > `nivel2`), so a row with only `nivel2` populated falls back to the chapter-total label.
  - INE renamed its Europe classification mid-series (UE27→UE28 and back) — `ue27_excl_espana`/`ue28_excl_espana` and `europa_no_ue27`/`europa_no_ue28` are both real raw labels; the pct-output step merges each pair into one `nationality_group` so a plot doesn't show a false discontinuity at the rename year.
  - `validate()` only prints a warning (stdout) if nationality sub-totals don't reconcile to the `total` row within ±5 — it does not halt the script. Check stdout, don't assume a clean run reconciled.

## `parse_ine_tabla28857.py` — convictions by sex × age × nationality

- **Input**: live fetch, `https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/28857.csv?nocab=1`. Same semicolon/Spanish-number format. Coverage 2017–2025, Chapter 8 headline total only (no crime subtype split, unlike 28716).
- **CLI**: `uv run python src/crime/parse_ine_tabla28857.py`
- **Output**: `data/processed/ine_condenados_28857_age_nationality.csv` — one row per (sex, nationality, age_band, year), 9 age bands (`18-20` … `71+`) plus `total`.
- **Quirks**:
  - **Nationality is continent-level only** (`africa`, `america`, …) — Morocco/Algeria or any other country **cannot** be isolated from this table. It exists as the general-population reference age-specific offending-rate curve for `compute_age_standardized_rate.py`'s (T78) age-standardization test, not for per-country drilldown.
  - `validate()` checks only that named age bands sum to the `total` age row (±5), for `nationality == "total"` — it does not cross-check nationality sub-totals (no country split exists at this granularity to check against).

## `parse_ses_odio_nationality.py` — hate-crime nationality (SES portal megatablas)

- **Input**: live fetch from `estadisticasdecriminalidad.ses.mir.es` (no auth/Cloudflare block, unlike the PDF host `interior.gob.es`). Two PX-format tables: `06019` (detenidos/investigados, 7 raw columns incl. leading `calificacion`) and `06013` (victimizaciones, 6 columns, no `calificacion`) — column layout is detected by **count**, not hardcoded per table. Coverage is **2021–2024 only**, confirmed to be a portal-wide limit (checked against a 3rd, non-nationality table `06001`), not specific to these two.
- **CLI**: `uv run python src/crime/parse_ses_odio_nationality.py` (loops both tables in one run)
- **Output**, per table (`detenidos`/`victimas`):
  - `data/raw/hate_crimes_ses_nacionalidad_{name}_2021-2024.csv` — raw rows filtered to `Comunidades autonomas == "TOTAL NACIONAL"` only (national level; all 18 CCAA/provincia rows discarded here, per project scope).
  - `data/raw/hate_crimes_ses_nacionalidad_{name}_summary_2021-2024.csv` — per (year, ámbito): `espana`, `total_nacionalidad`, `foreign`, `pct_spanish`.
- **Quirks**:
  - The "both sexes" aggregate label **differs by table**: `"Ambos sexos"` for `06019`, `"TOTAL sexo"` for `06013` — `06013` also carries 2 extra sex categories (`Persona juridica`, `Se desconoce`) that `06019` doesn't have.
  - New 2021+ ámbito labels not yet in `mir_parser.classify_odio_category`'s vocabulary are remapped here: `DISFOBIA`→`discapacidad`, `ISLAMOFOBIA`→`racismo_xenofobia` (folded in to keep the series simple, not a 1:1 semantic match).
  - `validate()` warns to **stderr** (not stdout, unlike the other 3 parsers) if nationality sub-totals don't reconcile to `"TOTAL nacionalidad"` within ±2 — doesn't halt.
  - Raw download is 19–24MB per table (89 countries × 18 CCAA × 3 sex × ~13 ámbitos × 4 years) before the national-level filter; don't expect the committed CSV size to reflect the fetch size.

## `parse_anuario_general_crime.py` — MIR Anuario general-crime PDFs

- **Input**: local PDFs already in the repo, `data/sources/anuario-estadistico/MIR_AnuarioEstadistico_{2016..2023}.pdf` (8 editions, 700–964 pages each). Missing editions are skipped with a printed notice, not an error. **Not** `extract_tables()` — these two source tables render without grid lines (only header/total rows are gridded), so extraction is `extract_text()` + per-line regex.
- **CLI**: `uv run python src/crime/parse_anuario_general_crime.py`
- **Output**: `data/raw/mir_anuario_general_crime_2015-2023.csv` — columns `year, category, metric, sex, count, source_edition, source_page, notes`.
  - `category` ∈ `{homicide, robbery, sexual_assault}` (`robbery` = "robos con fuerza en cosas" + "robos … violencia o intimidación" **summed**; excludes `hurto`/simple theft).
  - `metric` ∈ `{hechos_conocidos_total, detenciones_total, detenciones_foreign}`.
  - `sex` is `"all"` for the first two metrics (not sex-split in the source); `male`/`female`/`all` for `detenciones_foreign`.
- **Quirks**:
  - Two source tables per edition, located **by content**, not table number (numbering shifts across editions): table (a) is an ALL-nationality rolling 5-year window ("SERIE HISTÓRICA" pre-2020 / "EVOLUCIÓN" 2020+, both title formats tried); table (b) is FOREIGN-only, sex-split, 2-year window, nested under section "3.1.4 EXTRANJEROS" which has 2–3 sibling subsections whose cross-referencing intro prose can false-positive-match a naive title/keyword check — the real fix here is to attempt full extraction on every title-regex candidate page and keep the first one that actually yields rows, not to trust the title match alone.
  - A year can appear in up to 5 different editions (table a's rolling window); **the most recently published edition wins** on overlap — rows are overwritten, never averaged or summed.
  - `SEARCH_PAGE_LIMIT = 400` — pages beyond this are never scanned per PDF (all known tables live well before it; don't raise this without checking why a table isn't found first).
  - Some editions overflow the category rows onto a continuation page with no repeated header (2021 Anuario silently drops the robbery rows if only the located page is read) — the parser concatenates `extra_pages=2` trailing pages defensively.
  - Spanish-only counts are **not** source-reported directly for the foreign-split metric — `compute_general_crime_trends.py` (downstream, not this parser) derives them as `detenciones_total − detenciones_foreign`.

## Shared conventions across all 4

- Spanish INE/SES source format: `;`-delimited, `.` thousands separator, `,` decimal separator — all three HTTP-fetched parsers use `pandas.read_csv(sep=";", thousands=".", decimal=",")`.
- Every parser self-validates (sub-totals reconcile to a header "total" row) and **prints warnings rather than failing** — a clean run still needs its stdout/stderr checked, output files are written either way.
- None of the 4 scripts take CLI arguments; to change scope (years, tables, output paths) edit the module-level constants at the top of the file.
