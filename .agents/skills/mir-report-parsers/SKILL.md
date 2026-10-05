---
name: mir-report-parsers
description: |
  Reference for `src/parsers/*` — the PDF/text extractors for Ministerio
  del Interior (and related Ministerio de Igualdad) report series:
  `mir_parser.py` (sexual-violence Informe/Anuario, Balance de Criminalidad,
  Delitos de Odio — 4 modes, one file), `mir_violence_parser.py` +
  `mir_violence_extractor.py` (Violencia contra la Mujer "Violencia Sexual"
  chapter), `mir_migrant_nationality_parser.py` (perpetrator/victim
  nationality numerators across several reports), `feminicide_parser.py`
  (Delegación del Gobierno feminicide "ficha" series), and
  `macroencuesta_parser.py` (Macroencuesta victimization survey). Covers
  each parser's input format, CLI, output schema, and known quirks/gotchas
  so an agent doesn't have to re-derive them by reading 2000+ lines of
  source. Triggers when working on sexual-crime numerators, hate-crime
  typology (MIR's own series, not SES), feminicide counts, migrant-crime
  nationality numerators, or Macroencuesta prevalence/relationship figures.
  Replaces SIA-96/97/98/99/100. Does not cover crime-nationality
  denominators from INE/SES (see crime-parsers skill) or population/
  mortality/migration denominators (see demographics-parsers skill).
---

# mir-report-parsers — MIR/Igualdad PDF report parser reference

All of these extract from PDFs the agencies publish without a stable API —
most via `pdftotext`/`pdfplumber` text or table extraction, none via live
HTTP fetch inside the script (PDFs must already be on disk, several hosts
403/Cloudflare-block automated fetches). All MIR/Igualdad PDFs live under
`data/sources/` and must be downloaded manually first.

## `mir_parser.py` — sexual-violence Informe/Anuario, Balance, Odio (4 modes, one file, T19-T21/T26/T27)

Single file, one shared `MIRRecord`/`MIRReport`/`MIRDataset` Pydantic schema, four independent parser classes selected by `--mode`:

- **CLI**: `uv run python src/parsers/mir_parser.py --mode {informe|anuario|balance|odio} (--pdf-dir DIR | --pdf FILE [--year Y]) [--out-dir DIR]` (default out-dir `data/raw/`).
- **`InformeParser` (`--mode informe`)**: "Informe sobre Delitos contra la Libertad e Indemnidad Sexual en España" (dedicated annual report, 2019–present, most consistent table format). Output: `data/raw/sexual_crimes_mir_{year-range}.json`.
- **`AnuarioParser` (`--mode anuario`)**: "Anuario Estadístico del Ministerio del Interior" sexual-crimes chapter (2000–2021, broader document, variable format). Output: `data/raw/sexual_crimes_mir_anuario_{year-range}.json` — **separate file from Informe mode** (`_anuario` tag), since the two are independently-sourced, cross-validated series, not one dataset (B6/V13). Don't merge them into one file even though they share a schema.
- **`BalanceParser` (`--mode balance`)**: MIR "Balance de Criminalidad" quarterly reports, one national-aggregate table among hundreds of per-region pages — table's page position is **not fixed** (varies even between quarters of the same year), located by scanning for a line starting `"NACIONAL"`. **Critical**: these are cumulative year-to-date figures, not per-quarter increments — Q4 ("enero a diciembre") already IS the full-year total; naive-summing all 4 quarters overcounts ~2.4–2.5x (B24). `run_balance_batch()` therefore only emits the Q4 report per year and has its own batch loop — the generic `run_batch()` can't be reused here since all 4 quarters of a year infer to the same year and would trip its V22 year-collision guard. Output: `data/raw/sexual_crimes_mir_balance_{year-range}.json`.
- **`OdioParser` (`--mode odio`)**: "Informe sobre la evolución de los delitos de odio en España" (annual, 2014–2025 with gaps — 2013 has an unsupported layout, 2022 has no dedicated PDF, a real gap not a bug). Table page position varies by year and is located by content (`"HECHOS CONOCIDOS REGISTRADOS"` + `"RACISMO"` both present on the page), not a fixed page number. The table itself renders as an **infographic/chart, not a ruled table** — both `pdftotext -layout` (scrambles reading order) and `pdfplumber.extract_tables()` (needs ruling lines, none exist) fail; only `page.extract_words()` (word-position reconstruction) works. `classify_odio_category()` maps noisy ámbito labels to stable keys via **order-sensitive** substring checks (e.g. `ANTIGITANISMO` must be checked before generic `DISCRIMINACION`+`SEXO`+`GENERO`, which can coincidentally substring-match inside an `ORIENTACION SEXUAL` label) — reordering these checks can silently reclassify categories. Output filed under `hate_crimes_mir_{year-range}.json` (NOT `sexual_crimes_mir_*` — independently-sourced series, same reasoning as Anuario's tag) with headline total under a `total_hate_crimes` key (not `total_sexual_crimes`); the year-range stem (`_year_range_stem()`) preserves visible gaps (e.g. `2016-2021_2023`) rather than a plain first-last range that would hide the missing 2022.
- **Shared validation gate (V12)**: sum of crime subcategories must equal the headline total — a parse that violates this should be treated as a bug, not a source quirk.
- **Year-collision guard (V22)**: `run_batch()` raises if two input PDFs infer to the same year — pass `--pdf` explicitly per file rather than a mixed `--pdf-dir` if that happens (except Balance mode, which legitimately has 4 same-year PDFs and uses its own batch function instead).

## `mir_violence_parser.py` + `mir_violence_extractor.py` — Violencia contra la Mujer, "Violencia Sexual" chapter (2015–2019)

Different MIR publication from `mir_parser.py` despite the similar name: "Informe sobre la evolución de la violencia contra la mujer", `Violencia Sexual` chapter only, pages 52–57 by default (`MIR_ViolenceWomen_2015-2019.pdf`).

- **`mir_violence_parser.py`**: `parse_pdf(pdf_path, first_page=52, last_page=57)` extracts 5 tables via regex over `pdftotext` layout text — crime×year, crime×age, crime×nationality, location×year, relationship×year. Table 3 (nationality) lists the 6 crime types in a **different order** than Tables 1/2 (`CRIME_TYPES_NATIONALITY` vs `CRIME_TYPES`) — don't assume a shared ordering constant. Returns a dict of row-lists + a `validate_extraction()` result; does not write a file itself (stdout summary only).
- **`mir_violence_extractor.py`**: thin CLI wrapper — calls `parse_pdf()`, flattens all 5 tables into one tidy CSV (`source_table` 1–5 tags which table a row came from). **CLI**: `uv run python src/parsers/mir_violence_extractor.py <pdf_dir_or_file> [output_csv]` (default `data/raw/mir_violence_sexual_2015-2019.csv`). Directory mode globs `MIR_*.pdf` and deletes/rewrites the output CSV before the batch (not append-only across unrelated runs).

## `mir_migrant_nationality_parser.py` — perpetrator/victim nationality numerators (T26/T27/T83/T84)

Aggregates nationality breakdowns across **several different source documents**, not one PDF format:

- `parse_group_violence_2023()` — `MIR_GroupSexualViolence_2023.pdf` (study covers 2013–2017 cases).
- `parse_violence_women_2015_2019()` — `MIR_ViolenceWomen_2015-2019.pdf` (reused independently of `mir_violence_parser.py` — this extracts nationality-specific rows with its own regex, not a call into that module).
- `manual_entries_mir_informe_2023_2024()` — **hand-transcribed, not parsed from PDF**: the 2023/2024 Informe PDFs are Cloudflare-protected (interior.gob.es blocks automated fetches), so these figures come from press releases/official summaries, cross-checked against `violence_spain.csv`. Carries `confidence: "medium"` and an explicit "POLITICALLY SENSITIVE; verify from primary PDF" note on the foreign-perpetrator-percentage row — treat this function as the weakest-sourced part of the module, not equivalent to the PDF-parsed entries.
- `load_general_crime_anuario_rows()` — reshapes T84's already-parsed `data/raw/mir_anuario_general_crime_2015-2023.csv` (produced by `src/crime/parse_anuario_general_crime.py`, see crime-parsers skill) into foreign/Spanish numerator rows; no finer per-country breakdown is possible from this source (Anuario's foreign-split metric is Spanish-vs-foreign only, not per-country).
- **CLI**: `uv run python src/parsers/mir_migrant_nationality_parser.py` (no required args — combines all 4 sources above into one run).
- **Output**: `data/raw/migrant_crime_numerator.csv`, columns `row_id, report, report_year, data_year_start, data_year_end, crime_type, actor_role, nationality_group, iso2, count, pct, denominator, denominator_value, unit, source_table, confidence, notes`. Mixed-confidence by row — always check `confidence`/`notes`, don't treat the whole file as uniformly PDF-sourced.

## `feminicide_parser.py` — Delegación del Gobierno feminicide "ficha" series (T19/T20)

Annual PDF, 2003–present, one per year: "Mujeres Víctimas Mortales por Violencia de Género en España a manos de sus parejas o exparejas".

- **CLI**: `uv run python src/parsers/feminicide_parser.py (--pdf-dir DIR | --pdf FILE [--year Y]) [--out-dir DIR]` (default out-dir `data/raw/`).
- **Output**: `data/raw/feminicidios_delegacion_{min}-{max}.json`, Pydantic `FeminicideDataset` → one `FeminicideReport` per year. `source_document`/`source_page`/`confidence`/`verified` live **once per report**, not per category row (same shape as `mir_parser.py`'s `MIRReport`).
- **Two source-format eras, handled very differently**:
  - **2006–present**: numbered-table format (Tabla 2.1 region, 2.2 age, 2.3 country of birth, 2.4 relationship/cohabitation, 3.1 prior complaint, 3.2 protective measures, 3.3 restraining-order breach, 3.4 perpetrator suicide attempt) — fully parsed.
  - **2003–2005**: older "ficha resumen" chart-style layout — **only year + source metadata are extracted**; every breakdown field is left null. Don't assume these 3 years have the same completeness as 2006+.
- **Quirk — labels are matched against fixed vocabularies, not split from text**: region/age/nationality/relationship category names run together on one line with no reliable per-item delimiter (e.g. `"Andalucía Aragón Asturias, Principado de Balears, Illes..."`); the parser matches against vocabularies confirmed order-stable across every sampled year (2011–2026) and only parses out the unambiguous, whitespace-separated numeric values. If a future year reorders or renames categories, this ordering assumption breaks silently (wrong numbers, not an error) — worth spot-checking a new year's output against the source PDF, not just a clean exit code.

## `macroencuesta_parser.py` — Macroencuesta de Violencia contra la Mujer (T99)

Parses the "Violencia sexual fuera del ámbito de la pareja" chapter (Cap. 16 in both editions) of the Ministerio de Igualdad victimization survey — prevalence (lifetime/4yr/12mo/childhood, by severity tier in 2024 only) and victim-perpetrator relationship (familiar/conocido/desconocido).

- **CLI**: `uv run python src/parsers/macroencuesta_parser.py (--pdf-dir DIR | --pdf FILE [--year {2019,2024}]) [--out-dir DIR]`. Only 2019 and 2024 are implemented — those are the two waves with a full-report PDF on disk; the 2015 wave's relación figures are known only from a footnote quoted in the 2019 report and stay in `macroencuesta.md`'s prose, not this parser's output.
- **Output**: `data/raw/macroencuesta_2019-2024.json`. **Replaces** a prior hand-transcribed CSV (`data/raw/macroencuesta_relationship_2015-2024.csv`) — every figure was cross-checked against that transcription during development and matches exactly; this parser makes the existing figures re-runnable/auditable, it does not introduce new numbers.
- **Quirk**: both waves' relevant tables print as clean, consistently-ordered text via `pdfplumber.extract_text()` — `extract_tables()` returns the same kind of glued-cell mess as `mir_parser.py`'s relación table (`_locate_relationship_rows`), so this module deliberately uses text-regex extraction, not table objects. The 2019 and 2024 parsing logic differs enough to warrant two separate classes (`Macroencuesta2019Parser`/`Macroencuesta2024Parser`) rather than one with branches — 2024 adds severity-tier breakdowns the 2019 report doesn't have.

## `utils.py` — shared helpers

Deduplicated from what used to be copy-pasted with small divergences across the files above:

- `extract_text(pdf_path, layout=False, first_page=None, last_page=None, timeout=60)` — `pdftotext` subprocess wrapper.
- `write_csv_rows(path, rows, fieldnames, mode="a", ...)` — `csv.DictWriter`, writes header only if the file is currently empty (works for both incremental-append and single-overwrite call patterns).
- `parse_es_number(s)` — Spanish-formatted number (`.` thousands, `,` decimal) → `float`, returns `None` for `-`/`—`/`N/A`/empty.
- `cli_require_arg(argv, usage_lines, min_len=2)` — argv length guard + usage message + `exit(1)`.

`mir_parser.py`, `feminicide_parser.py`, and `macroencuesta_parser.py` use `pdfplumber` directly instead (table-object access, not just text) — `utils.py` is shared by the text-regex-only parsers (`mir_violence_parser.py`, `mir_migrant_nationality_parser.py`, `mir_violence_extractor.py`).

## Downstream consumers (not parsers themselves, but read these outputs)

- `src/sexual_crimes/build_dashboard_data.py`, `plot_sexual_crime_trends.py` — consume `mir_parser.py`'s Informe/Anuario output and `macroencuesta_parser.py`'s output.
- `src/feminicides/compute_feminicide_rates.py`, `build_dashboard_data.py` — consume `feminicide_parser.py`'s output plus a population denominator (see demographics-parsers skill).
