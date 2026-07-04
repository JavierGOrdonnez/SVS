# Source: Ministerio del Interior — Informes sobre la Evolución de los Delitos de Odio en España

**Publisher:** Ministerio del Interior / Secretaría de Estado de Seguridad (ONDOD — Oficina Nacional de Delitos de Odio, since 2023)
**Series name:** Informe sobre la evolución de los delitos e incidentes de odio en España
**Coverage:** Annual; police-recorded ("hechos conocidos") hate crimes/incidents by ámbito (motivation)
**Available from:** 2013 (series start per publisher); PDFs staged in this repo: 2016–2021, 2023 (**2022 has no dedicated PDF — genuine publication gap**, see below)

## Access

| Resource | URL |
|---|---|
| Series landing page (all editions) | https://interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/informe-sobre-la-evolucion-de-los-delitos-de-odio-en-espana/ |
| 2024 report PDF (most recent, not yet staged in `data/sources/`) | https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/INFORME_Evolucion_delitos_de_odio_2024.pdf |
| Portal Estadístico Criminalidad (canonical hub, all MIR series) | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/publicaciones.html |
| ONDOD publications | https://oficinanacional-delitosdeodio.ses.mir.es/publico/ONDOD/ |

The 2016–2021 and 2023 edition PDFs staged in `data/sources/MIR_InformeDelitosOdio_{year}.pdf` were sourced from the landing page above; per-edition direct URLs were not individually re-confirmed live for this pass (only the 2024 URL was, via `discurso_odio_inmigracion_espana.md` §2.1) — re-fetch from the landing page if a PDF needs replacing.

## Parser

`src/parsers/mir_parser.py`'s `OdioParser` (`--mode odio`) extracts the "Hechos conocidos registrados" typology table — one row per ámbito (motivation), 2-3 year columns per edition. Run via:

```
uv run python src/parsers/mir_parser.py --mode odio --pdf-dir data/sources [--out-dir data/raw]
```

Output: `data/raw/hate_crimes_mir_2016-2021_2023.json` (filename reflects the real, non-contiguous coverage — the `2016-2021_2023` stem, not a misleading `2016-2023`).

**Extraction method:** the table is chart/infographic-rendered — neither `pdftotext -layout` nor `pdfplumber.extract_tables()` recovers it reliably. The parser uses `pdfplumber.extract_words()` (word bounding boxes) clustered into rows by y-position (`top`) proximity (3pt tolerance — ámbito-to-ámbito gaps are always ≥10pt; a label/numbers sub-row split is always ≤1-2pt), then reads the first N integer-only tokens left-to-right per row (N = number of year columns, detected dynamically from the header row's "20XX" tokens, not hardcoded — 2 cols for 2016-2020, 3 cols for 2021 and 2023, since those two editions add extra backward-comparison columns). The page itself is located by content match (`"HECHOS CONOCIDOS REGISTRADOS"` / `"RACISMO"`), not a fixed page number — it moves between editions (2016: p14 … 2023: p12).

## Key figures verified from primary sources (directly parsed, all years hand-cross-checked)

### 2016
- **Total hate crimes: 1,272** (single-tier total — no "infracciones administrativas" split existed yet)
- Racismo/xenofobia: 416 (largest ámbito)
- Discapacidad: 262
- Ideología: 259
- Orientación/identidad sexual: 230
- Creencias o prácticas religiosas: 47
- Discriminación por sexo/género: 41
- Aporofobia: 10
- Antisemitismo: 7
- Ámbito sum = 1,272 = total (exact)

### 2017
- **Total hate crimes: 1,419**
- Racismo/xenofobia: 524; Ideología: 446; Orientación/identidad sexual: 271; Creencias/prácticas religiosas: 103; **Discapacidad: 23** (see methodology-break caveat below); Discriminación sexo/género: 35; Aporofobia: 11; Antisemitismo: 6
- Ámbito sum = 1,419 = total (exact)

### 2018
- **Total hate crimes: 1,598**
- Racismo/xenofobia: 531; Ideología: 596; Orientación/identidad sexual: 259; Creencias/prácticas religiosas: 69; Discapacidad: 25; Discriminación sexo/género: 71; two **new ámbitos introduced**: Discriminación generacional (16), Discriminación por razón de enfermedad (8); Aporofobia: 14; Antisemitismo: 9
- Ámbito sum = 1,598 = total (exact)

### 2019
- **Total delitos e incidentes de odio (headline): 1,706** — first year the 3-tier structure appears
- Total delitos (sum of ámbitos): 1,598; Infracciones administrativas y resto de incidentes: 108 (1,598 + 108 = 1,706, exact)
- Racismo/xenofobia: 515; Ideología: 596; Orientación/identidad sexual: 278; Creencias/prácticas religiosas: 66; Discapacidad: 26; Discriminación sexo/género: 69; Discriminación generacional: 9; Discriminación por enfermedad: 8; **new ámbito: Antigitanismo: 14** (report's own prose flags this as a "nuevo ámbito" this edition)
- Ámbito sum = 1,598 = total delitos (exact)

### 2020
- **Total delitos e incidentes de odio (headline): 1,401**
- Total delitos: 1,334; Infracciones administrativas: 67 (1,334 + 67 = 1,401, exact)
- Racismo/xenofobia: 485; Ideología: 326; Orientación/identidad sexual: 277; Creencias/prácticas religiosas: 45; Discapacidad: 44; Discriminación sexo/género: 99; Antigitanismo: 22; Discriminación por enfermedad: 13; Discriminación generacional: 10; Aporofobia: 10; Antisemitismo: 3
- Ámbito sum = 1,334 = total delitos (exact)

### 2021
- **Total delitos e incidentes de odio (headline): 1,802**
- Total delitos: 1,724; Infracciones administrativas: 78 (1,724 + 78 = 1,802, exact)
- Racismo/xenofobia: 639; Orientación/identidad sexual: 466; Ideología: 326; Discriminación sexo/género: 107; Creencias/prácticas religiosas: 63; Discapacidad: 28; Antigitanismo: 18; Discriminación por enfermedad: 21; Discriminación generacional: 35; Aporofobia: 10; Antisemitismo: 11
- Ámbito sum = 1,724 = total delitos (exact)
- This edition and 2023 carry 3 year-columns (own year + 2 prior years of backward comparison) instead of 2.

### 2022 — **no dedicated PDF exists (publication gap)**
No standalone `Informe delitos de odio 2022` PDF was located or staged. Partially recoverable from the 2023 edition's own backward-comparison columns (2023's report shows 2021/2022/2023 side by side): 2022 **total delitos = 1,796**, **total delitos e incidentes de odio (headline) = 1,869** (1,796 + 73 infracciones administrativas, by subtraction). These figures are **not** synthesized into a full `MIRReport` for 2022 in `hate_crimes_mir_2016-2021_2023.json` — deliberately, to avoid mixing a primary-sourced report (own year's dedicated PDF, full ámbito breakdown) with a secondary-sourced one (another year's retrospective column, headline totals only, no ámbito breakdown). The gap is real and visible in the output filename (`2016-2021_2023`, not `2016-2023`).

### 2023
- **Total delitos e incidentes de odio (headline): 2,268** (+21.35% vs 2022, per the report's own prose)
- Total delitos: 2,150; Infracciones administrativas: 118 (2,150 + 118 = 2,268, exact)
- Racismo/xenofobia: 856; Orientación/identidad sexual: 522; Ideología: 352; Discriminación sexo/género: 206; Creencias/prácticas religiosas: 55; Discapacidad: 49; Antigitanismo: 37; Antisemitismo: 23; Aporofobia: 18; Discriminación generacional: 21; Discriminación por enfermedad: 11
- Ámbito sum = 2,150 = total delitos (exact)
- Own report's retrospective column independently confirms 2021's total delitos e incidentes = 1,802 — matching the 2021 edition's own dedicated-PDF figure exactly (cross-publication consistency check, unlike the retroactive-restatement gotcha below which found the opposite for a within-year figure).

## Out-of-scope PDFs staged in the same source family

Two other PDFs live alongside the annual series in `data/sources/` but are **not parsed** by `OdioParser` (different structure entirely):

- `MIR_EncuestaVictimasOdio_2021.pdf` — a 77-page victim/witness survey report (part of the EU "EStAR" project), with ~20+ small named result tables ("Tabla 18", "Tabla 19", …) scattered across the document, not the single consistent typology-table format this parser targets. Would need a dedicated parser if ever pursued.
- `MIR_PlanAccionOdio.pdf` — the "II Plan de Acción de Lucha contra los Delitos de Odio" policy document, 33 pages of prose with no statistical tables.

## Category list (normalized keys, via `classify_odio_category`)

`total_hate_crimes` (report headline) / `total_delitos` (sum of ámbitos) / `infracciones_administrativas` (2019+) / `racismo_xenofobia` / `orientacion_identidad_sexual_genero` / `ideologia` / `discapacidad` / `discriminacion_sexo_genero` / `creencias_practicas_religiosas` / `aporofobia` / `antisemitismo` / `antigitanismo` (2019+) / `discriminacion_generacional` (2018+) / `discriminacion_enfermedad` (2018+)

## Critical caveats

1. **2017 "discapacidad" methodology break**: the ámbito labeled `DISCAPACIDAD` in 2016 (262) is renamed `DIVERSIDAD FUNCIONAL` in 2017 and reports 23 — a −91.2% drop with no real-world equivalent. The 2017 report's own prose attributes this to a methodology/definition change, not an actual collapse in incidents. `classify_odio_category` maps `DISCAPACIDAD` / `DIVERSIDAD FUNCIONAL` / `PERSONA CON DISCAPACIDAD` (2018-2020) / `DELITOS DE ODIO CONTRA PERSONAS CON DISCAPACIDAD` (2021, 2023) all to the same key (`discapacidad`) for series continuity, but the pre/post-2017 values are **not comparable** without this caveat attached — same class of issue as the sexual-crimes series' LO 10/2022 break (see `mir_informes_delitos_sexuales.md` caveat 1).
2. **New ámbitos introduced mid-series, not retrofitted to earlier years**: Discriminación generacional and Discriminación por razón de enfermedad first appear in 2018; Antigitanismo first appears in 2019 (report's own text flags it as a "nuevo ámbito"). Earlier years simply have no row for these — treat as "not tracked yet," not "zero incidents."
3. **3-tier total structure, 2019+ only**: 2016-2018 have a single TOTAL row equal to the ámbito sum. From 2019 on, TOTAL DELITOS (ámbito sum) and INFRAC. ADM. Y RESTO INCIDENTES (administrative infractions + residual incidents, excluded from the ámbito sum) combine into TOTAL DELITOS E INCIDENTES DE ODIO (the report's actual headline number). `total_hate_crimes` in the dataset is always this headline figure; for 2016-2018 it equals `total_delitos` since no infracciones-administrativas tier exists yet.
4. **2022 publication gap**: no dedicated annual PDF exists for 2022. Partial figures are recoverable only from the 2023 edition's own backward-comparison column (see above) — headline totals only, no ámbito breakdown, and deliberately not merged into a full `MIRReport` to avoid conflating primary- and secondary-sourced years.
5. **Retroactive-restatement risk (general)**: as with the Anuario series (`mir_informes_delitos_sexuales.md`, B9), a later year's backward-comparison column for a prior year is not guaranteed to match that prior year's own dedicated report bit-for-bit in every case; this parser always treats each year's **own** dedicated PDF as authoritative and only uses another edition's retrospective column as a documented fallback for the 2022 gap above (where it was spot-checked to agree with 2021's own report exactly, giving some confidence in its reliability, but it remains secondary-sourced).
6. **Chart-rendered table extraction**: `pdftotext -layout` and `pdfplumber.extract_tables()` both fail on this table (it's rendered as an infographic/chart, not a bordered grid). `OdioParser` uses word-position clustering (`extract_words()` + y-tolerance row reconstruction) instead — see Parser section above.
7. **Mixed thousands-separator formatting within the same table**: some totals render as plain digit strings (e.g. `1476`, no separator) while others in the same row/table use Spanish dot-grouping (e.g. `1.598`) — confirmed directly in the 2019 edition's own TOTAL DELITOS row. The parser's integer-token regex accepts both forms; an earlier draft regex matching only the dot-grouped form would have silently dropped or misparsed any no-separator total.
