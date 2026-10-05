---
name: parsers-index
description: |
  Single entry point indexing all 14 raw-source-to-tidy-output parser
  scripts in this repo (path, source, domain, owning domain skill, output
  file) and routing to the one of three domain skills — crime-parsers,
  demographics-parsers, mir-report-parsers — that documents it in depth.
  Triggers whenever the task names a specific parser script, a source
  table/report, or an output file and you need to know which domain skill
  to load next; also use it to confirm a script IS one of the documented
  parsers before assuming it's undocumented. Does not itself cover input
  format/CLI/quirks — load the owning skill for that.
---

# parsers-index — lookup table, route to a domain skill

Covers only the 14 scripts that turn a raw external source (INE/Eurostat/SES
API or MIR/Igualdad PDF) into a tidy repo output file. Downstream
aggregation/dashboard-build scripts (`compute_*`, `analyze_*`,
`build_dashboard_data.py`, etc.) are **not** parsers and are not indexed
here — see `data/PIPELINE.md` for the full script-level map including those.

| path | source | domain skill | output |
|---|---|---|---|
| `src/crime/parse_ine_tabla28716.py` | INE table 28716, live fetch | [crime-parsers](../crime-parsers/SKILL.md) | `data/processed/ine_condenados_28716_sexual_crimes.csv`, `..._nationality_pct.csv` |
| `src/crime/parse_ine_tabla28857.py` | INE table 28857, live fetch | [crime-parsers](../crime-parsers/SKILL.md) | `data/processed/ine_condenados_28857_age_nationality.csv` |
| `src/crime/parse_anuario_general_crime.py` | MIR Anuario PDFs (local, `data/sources/anuario-estadistico/`) | [crime-parsers](../crime-parsers/SKILL.md) | `data/raw/mir_anuario_general_crime_2015-2023.csv` |
| `src/crime/parse_ses_odio_nationality.py` | SES portal megatablas 06019/06013, live fetch | [crime-parsers](../crime-parsers/SKILL.md) | `data/raw/hate_crimes_ses_nacionalidad_{detenidos,victimas}_2021-2024.csv` + `..._summary_...csv` |
| `src/analysis/parse_ine_population.py` | INE table 56934, manual CSV download | [demographics-parsers](../demographics-parsers/SKILL.md) | `data/processed/population_spain_estimates.csv`, `population_spain_midyear_5yr.csv` |
| `src/analysis/parse_ine_population_nationality.py` | INE table 56936, manual CSV download | [demographics-parsers](../demographics-parsers/SKILL.md) | `data/processed/population_spain_nationality.csv` |
| `src/mortality/parse_ine_mortality.py` | INE table 7947, manual JSON dump (`wstempus` API) | [demographics-parsers](../demographics-parsers/SKILL.md) | caller-named CSV, conventionally `data/processed/mortality_spain_ine_ecm.csv` |
| `src/migration/parse_eurostat_migration_cohort.py` | Eurostat `migr_imm1ctz`/`migr_pop1ctz`, manual JSONL download | [demographics-parsers](../demographics-parsers/SKILL.md) | appends to `data/raw/migration_spain.csv` |
| `src/parsers/mir_parser.py` (4 modes: `informe`/`anuario`/`balance`/`odio`) | MIR Informe/Anuario/Balance de Criminalidad/Delitos de Odio PDFs (local) | [mir-report-parsers](../mir-report-parsers/SKILL.md) | `data/raw/sexual_crimes_mir_{range}.json`, `..._anuario_{range}.json`, `..._balance_{range}.json`, `data/raw/hate_crimes_mir_{range}.json` |
| `src/parsers/mir_violence_parser.py` | `MIR_ViolenceWomen_2015-2019.pdf` (local) | [mir-report-parsers](../mir-report-parsers/SKILL.md) | none (stdout only — library module for `mir_violence_extractor.py`) |
| `src/parsers/mir_violence_extractor.py` | same PDF, via `mir_violence_parser.parse_pdf()` | [mir-report-parsers](../mir-report-parsers/SKILL.md) | `data/raw/mir_violence_sexual_2015-2019.csv` |
| `src/parsers/mir_migrant_nationality_parser.py` | `MIR_GroupSexualViolence_2023.pdf` + `data/sources/reference/` PDFs + manual entries + `mir_anuario_general_crime_2015-2023.csv` | [mir-report-parsers](../mir-report-parsers/SKILL.md) | `data/raw/migrant_crime_numerator.csv` |
| `src/parsers/feminicide_parser.py` | Delegación del Gobierno feminicide PDFs, 2003–present (local) | [mir-report-parsers](../mir-report-parsers/SKILL.md) | `data/raw/feminicidios_delegacion_{min}-{max}.json` |
| `src/parsers/macroencuesta_parser.py` | `Macroencuesta_{2019,2024}.pdf` (local) | [mir-report-parsers](../mir-report-parsers/SKILL.md) | `data/raw/macroencuesta_2019-2024.json` |

## Shared helper

`src/parsers/utils.py` — `extract_text`/`write_csv_rows`/`parse_es_number`/`cli_require_arg`, used by the text-regex parsers under `src/parsers/` (not a parser itself; documented in [mir-report-parsers](../mir-report-parsers/SKILL.md)).
