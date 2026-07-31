# Source: Ministerio del Interior — Informes sobre la Evolución de los Delitos de Odio en España

**Publisher:** Ministerio del Interior / Secretaría de Estado de Seguridad (ONDOD — Oficina Nacional de Delitos de Odio, since 2023)
**Series name:** Informe sobre la evolución de los delitos e incidentes de odio en España
**Coverage:** Annual; police-recorded ("hechos conocidos") hate crimes/incidents by ámbito (motivation)
**Available from:** 2014 (first year staged here in the normalized source layout); PDFs staged in this repo: 2014–2016, 2017–2025 (with a few layout/cross-publication caveats, see below)

## Access

| Resource | URL |
|---|---|
| Series landing page (all editions) | https://interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/informe-sobre-la-evolucion-de-los-delitos-de-odio-en-espana/ |
| 2024 report PDF (most recent, not yet staged in `data/sources/`) | https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/INFORME_Evolucion_delitos_de_odio_2024.pdf |
| Portal Estadístico Criminalidad (canonical hub, all MIR series) | https://estadisticasdecriminalidad.ses.mir.es/publico/portalestadistico/publicaciones.html |
| ONDOD publications | https://oficinanacional-delitosdeodio.ses.mir.es/publico/ONDOD/ |

The staged annual PDFs now live under `data/sources/odio/informes-mir/MIR_InformeDelitosOdio_{year}.pdf` and were sourced from the landing page above; per-edition direct URLs were not individually re-confirmed live for this pass (only the 2024 URL was, via `discurso_odio_inmigracion_espana.md` §2.1) — re-fetch from the landing page if a PDF needs replacing.

Very interesting research on why Pais Vasco has "more" hate-based crimes: it has stronger protocols + a very active NGO network. https://www.google.com/search?q=delitos+de+odio+tasa+alta+en+pais+vasco&client=ubuntu-sn&hs=frX&sca_esv=31a84013ae363f98&channel=fs&sxsrf=APpeQnty7ErroM5Sf-jj1xe_LrAvlSEgTA%3A1784551827330&fbs=ABfTbFVyMZGZf1hfvX9uKjN_-G8cY2oODYyTyZk24Xz37_7FQ0Kuh3jfnRqiKzI7KrGsO-a7vPN0oJUPXgT9BPYDfgnNyZgeXjHMCv7f4G7IWNhEcC49wBJI-L3x_dOfEKpVbUZwPZED7VgF0N_HgfGIzmpn0aTB0U82TY4K0Lq_vSHv3mMEDvfkH-4EliBhKflhow8Fu6iPrNz7A5hkc6U0S2Y1GoyVqw&aep=1&ntc=1&cs=1&sa=X&ved=2ahUKEwjd34DOpeGVAxUq9gIHHZwuKiAQ2J8OegQIExAD&biw=1864&bih=963&dpr=1&mstk=AUtExfAwdmAL2Ky8l-idm6gmLZqkAFXFiPp8HjDeCoCuGwMQRLWprR93aL4sq4XChIBDbA70iYgK3xuT2MK4S9vH-ODEO77WQcVVdUBBwyJrY7H3k5Wk4sySfAoPnBibBzcHhxpEMhNfc-4k2z_U8SW0BluIsh__W5X3DYmX7XWXYf7TqMc5yEK2XM2pv77usYrQRnQ5V-zsYlgldlnyLmpc_zT2rpQuxuSUANIYdsLtn8jZEN7kqPLdWUsgosM4Ez1CjB0I5ZRJx61aRw&csuir=1&mtid=eRxeaurWF7jKi-gPvtaooQY&udm=50

## Parser

`src/parsers/mir_parser.py`'s `OdioParser` (`--mode odio`) extracts the "Hechos conocidos registrados" typology table — one row per ámbito (motivation), 2-3 year columns per edition. Run via:

```
uv run python src/parsers/mir_parser.py --mode odio --pdf-dir data/sources [--out-dir data/raw]
```

Output: `data/raw/hate_crimes_mir_2014-2025.json` (filename now reflects continuous coverage through 2025; 2013 remains excluded as an unsupported layout).

**Extraction method:** the table is chart/infographic-rendered — neither `pdftotext -layout` nor `pdfplumber.extract_tables()` recovers it reliably. The parser uses `pdfplumber.extract_words()` (word bounding boxes) clustered into rows by y-position (`top`) proximity (3pt tolerance — ámbito-to-ámbito gaps are always ≥10pt; a label/numbers sub-row split is always ≤1-2pt), then reads the first N integer-only tokens left-to-right per row (N = number of year columns, detected dynamically from the header row's "20XX" tokens, not hardcoded — 2 cols for 2016-2020, 3 cols for 2021 and 2023, since those two editions add extra backward-comparison columns). The page itself is located by content match (`"HECHOS CONOCIDOS REGISTRADOS"` / `"RACISMO"`), not a fixed page number — it moves between editions (2016: p14 … 2023: p12).

## Key figures verified from primary sources (directly parsed, all years hand-cross-checked)

2013 is present in the archive but is not parsed here: its PDF layout is not the annual typology report shape this parser targets, so it is intentionally skipped in code.

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

### 2022
The staged 2022 annual PDF now exists and parses cleanly. Its headline totals are 1,869 total incidents and 1,796 total delitos, with 73 administrative incidents; it should be treated as a normal year in the annual series.

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

`total_hate_crimes` (report headline) / `total_delitos` (sum of ámbitos) / `infracciones_administrativas` (2019+) / `racismo_xenofobia` / `orientacion_identidad_sexual_genero` / `ideologia` / `discapacidad` (label renamed again to `DISFOBIA` in the 2021+ SES portal data, see below — same key, same rename lineage as `DISCAPACIDAD`→`DIVERSIDAD FUNCIONAL`) / `discriminacion_sexo_genero` / `creencias_practicas_religiosas` / `aporofobia` / `antisemitismo` / `antigitanismo` (2019+) / `discriminacion_generacional` (2018+) / `discriminacion_enfermedad` (2018+) / `islamofobia` (2024+, its own category — first year Islamophobia was broken out separately per the 2024 report's own prose)

## Nationality data: a separate source (SES portal megatablas, 2021-2024), and two closed leads

The PDF reports parsed above (`OdioParser`) give the typology/ámbito series but
carry **no nationality breakdown** — that table exists, but only in the
PDFs' own charts (not machine-extracted here) and only for 2021-2024
editions. Nationality (Spanish vs. per-country) by ámbito, for both
detainees/investigated and victims, is instead sourced from a **different,
much better** place, found and validated in this session:

**Source: the Interior Ministry's own statistics portal**,
`estadisticasdecriminalidad.ses.mir.es` — not a PDF, a live queryable
PC-Axis "megatabla" system, downloadable as CSV with no auth and no
Cloudflare block (unlike interior.gob.es, the PDF host). It hosts a family
of 20 tables (`06001`-`06020`) covering hechos-conocidos/esclarecidos,
victimizaciones, and detenciones/investigados, each at CCAA-or-provincia
granularity. This project uses two, at national level only:

| Table | Content | Download |
|---|---|---|
| `06019` | Detenidos/investigados × nacionalidad × ámbito × sexo × período | `https://estadisticasdecriminalidad.ses.mir.es/sec/jaxiPx/files/_px/es/csv_bdsc/Datos6/l0/06019.px_bdsc` |
| `06013` | Victimizaciones × nacionalidad × ámbito × sexo × período | `https://estadisticasdecriminalidad.ses.mir.es/sec/jaxiPx/files/_px/es/csv_bdsc/Datos6/l0/06013.px_bdsc` |

Parsed by `src/crime/parse_ses_odio_nationality.py` → `data/raw/hate_crimes_ses_nacionalidad_{detenidos,victimas}_2021-2024.csv` (full per-country detail, national rows only) and `..._summary_2021-2024.csv` (per year/ámbito: España count, total, foreign, % Spanish). Tested in `tests/test_ses_odio_nationality.py`.

**Coverage is 2021-2024 only — confirmed empirically, not assumed.** A
second, non-nationality table from the same family (`06001`, hechos
conocidos — the same metric `OdioParser` already gets from PDFs back to
2016) is *also* 2021-2024-only when queried through this portal system, so
the cutoff is a portal-wide limitation, not specific to the nationality
tables. Two candidate sources that might explain *why* (a
`Metodologia_estadistica_ONDOD.pdf` methodology doc, and an "Interior
moderniza su Portal Estadístico de Criminalidad" press article) were both
unreachable (503 / Cloudflare 403) when checked — so the reason is not
independently confirmed from an official document, only the empirical
cutoff itself.

**Validated against known figures** (exact matches, both independent of
each other): 2023 detainees, all ámbitos, national: 1,161 total / 914
España = **78.7%** Spanish (matches the previously prose-only "78.73%"
figure in `discurso_odio_inmigracion_espana.md` §2.1). 2023 victims, all
ámbitos: **62.2%** Spanish (matches that same doc's "62.15%"). 2024
detainees total = 901 (matches the "905 arrested/investigated" prose
figure, small rounding difference).

**New finding, not previously known in this repo:** querying `06019` for
`Ámbito = ORIENTACIÓN SEXUAL E IDENTIDAD DE GÉNERO` (2023, national) gives
**194 Spanish / 269 total = 72.1% Spanish** — a real, national,
OSIG-specific aggressor-nationality figure. No PDF or press source
surfaces this breakdown; it only exists in this raw portal table.

### Two leads chased and closed (so they aren't re-checked)

- **`MIR_BalanceCriminalidad_*.pdf`** (the quarterly "Balance de
  Criminalidad" series, used elsewhere in this repo for sexual crimes'
  row 5/5.1/5.2 via `BalanceParser`): the 2023 Q4 edition (501 pages) was
  full-text scanned directly for "nacionalidad" and "delitos de odio" —
  **zero matches**. It is a pure region/province × general-crime-type-count
  series; no nationality breakdown, no hate-crime row, anywhere.
- **INE's numbered "Condenados" table family** (operation 213, the same
  family as table `28716` already used for sexual crimes in
  `src/crime/parse_ine_tabla28716.py`): its general (non-sexual-specific)
  sibling, table **26014** ("Delitos según nacionalidad"), was fetched live
  — its crime-type hierarchy (`nivel2`) has no "Contra la Constitución"
  (Título XXI CP, where the hate aggravante and Art. 510 CP hate-speech
  offense live) category at all; it is absorbed into an undifferentiated
  "Resto de delitos" bucket with no way to isolate it. INE's full catalog
  of 112 statistical operations (`OPERACIONES_DISPONIBLES` API) was also
  checked directly: the only justice-adjacent ones are Juzgados de Paz,
  Población Condenada Adulta/Menor, and Violencia Doméstica/Género — **no
  dedicated hate-crime operation exists at INE.**

### No official conviction (condenados) series exists for hate crimes

Confirmed from three independent angles: the INE check above (no operation,
no category); the SES portal (which only publishes police-recorded
hechos/víctimas/detenidos-investigados — a judicial outcome is simply not
what this system tracks); and prior research on the OSIG ámbito
specifically that reached the same conclusion. The closest available data
point is a one-off academic study — Giménez-Salinas Framis, A. et al.,
*"Análisis de casos y sentencias en materia de racismo, xenofobia,
LGTBIfobia y otras formas de intolerancia 2018-2022"* (OBERAXE/Ministerio de
Inclusión, 2023) — which analyzed 177 court sentences nationwide and found,
among 26 OSIG-motivated defendants with known nationality, 18 (69.2%)
Spanish. This is a small, sentencing-stage-filtered sample spanning five
years, not an official annual series — cite it as indicative, not as "the"
hate-crime conviction rate by nationality.

## Critical caveats

1. **2017 "discapacidad" methodology break**: the ámbito labeled `DISCAPACIDAD` in 2016 (262) is renamed `DIVERSIDAD FUNCIONAL` in 2017 and reports 23 — a −91.2% drop with no real-world equivalent. The 2017 report's own prose attributes this to a methodology/definition change, not an actual collapse in incidents. `classify_odio_category` maps `DISCAPACIDAD` / `DIVERSIDAD FUNCIONAL` / `PERSONA CON DISCAPACIDAD` (2018-2020) / `DELITOS DE ODIO CONTRA PERSONAS CON DISCAPACIDAD` (2021, 2023) all to the same key (`discapacidad`) for series continuity, but the pre/post-2017 values are **not comparable** without this caveat attached — same class of issue as the sexual-crimes series' LO 10/2022 break (see `mir_informes_delitos_sexuales.md` caveat 1).
2. **New ámbitos introduced mid-series, not retrofitted to earlier years**: Discriminación generacional and Discriminación por razón de enfermedad first appear in 2018; Antigitanismo first appears in 2019 (report's own text flags it as a "nuevo ámbito"). Earlier years simply have no row for these — treat as "not tracked yet," not "zero incidents."
3. **3-tier total structure, 2019+ only**: 2016-2018 have a single TOTAL row equal to the ámbito sum. From 2019 on, TOTAL DELITOS (ámbito sum) and INFRAC. ADM. Y RESTO INCIDENTES (administrative infractions + residual incidents, excluded from the ámbito sum) combine into TOTAL DELITOS E INCIDENTES DE ODIO (the report's actual headline number). `total_hate_crimes` in the dataset is always this headline figure; for 2016-2018 it equals `total_delitos` since no infracciones-administrativas tier exists yet.
4. **2022 publication gap**: no dedicated annual PDF exists for 2022. Partial figures are recoverable only from the 2023 edition's own backward-comparison column (see above) — headline totals only, no ámbito breakdown, and deliberately not merged into a full `MIRReport` to avoid conflating primary- and secondary-sourced years.
5. **Retroactive-restatement risk (general)**: as with the Anuario series (`mir_informes_delitos_sexuales.md`, B9), a later year's backward-comparison column for a prior year is not guaranteed to match that prior year's own dedicated report bit-for-bit in every case; this parser always treats each year's **own** dedicated PDF as authoritative and only uses another edition's retrospective column as a documented fallback for the 2022 gap above (where it was spot-checked to agree with 2021's own report exactly, giving some confidence in its reliability, but it remains secondary-sourced).
6. **Chart-rendered table extraction**: `pdftotext -layout` and `pdfplumber.extract_tables()` both fail on this table (it's rendered as an infographic/chart, not a bordered grid). `OdioParser` uses word-position clustering (`extract_words()` + y-tolerance row reconstruction) instead — see Parser section above.
7. **Mixed thousands-separator formatting within the same table**: some totals render as plain digit strings (e.g. `1476`, no separator) while others in the same row/table use Spanish dot-grouping (e.g. `1.598`) — confirmed directly in the 2019 edition's own TOTAL DELITOS row. The parser's integer-token regex accepts both forms; an earlier draft regex matching only the dot-grouped form would have silently dropped or misparsed any no-separator total.
