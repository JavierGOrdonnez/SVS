# Source: Delegación del Gobierno contra la Violencia de Género — Femicide Registry

**Publisher:** Ministerio de Igualdad — Delegación del Gobierno contra la Violencia de Género  
**Series name:** Estadística de Víctimas Mortales por Violencia de Género  
**Coverage:** Annual; partner/ex-partner homicides only (LO 1/2004 scope)  
**Available from:** 2003 (first year of official registry)  
**Pre-2003:** INE series v02001.px extends to 1999 (see `ine_poblacion_femicidios.md`)

## Definition

Counts women killed by current or former intimate partner. Does **not** include:
- Killings by other family members
- Killings by acquaintances or strangers
- "Vicarious" killings of children

Feminicidio.net uses a broader definition (all female homicides); their annual figures are ~2× higher.

## Access

| Resource | URL |
|---|---|
| Main landing page (all years) | https://violenciagenero.igualdad.gob.es/violenciaencifras/victimasmortales/fichamujeres/ |
| Instituto de la Mujer tabular series | https://www.inmujeres.gob.es/MujerCifras/Violencia/VictimasMortalesVG.htm |
| INE tabular series 1999–present | https://www.ine.es/jaxi/Tabla.htm?path=%2Ft00%2Fmujeres_hombres%2Ftablas_1%2Fl0%2F&file=v02001.px&L=0 |
| 2024 ficha (updated 14/02/2025) | https://violenciagenero.igualdad.gob.es/wp-content/uploads/VMujeres_2024_act_14_02_2025.pdf |
| 2024 monthly update Nov | https://violenciagenero.igualdad.gob.es/wp-content/uploads/VMortales_2024_11_25.pdf |
| XVIII Informe Anual Observatorio 2024 | https://violenciagenero.igualdad.gob.es/violenciaencifras/observatorio/informesanuales/xviii-informe-anual-del-observatorio-estatal-de-violencia-sobre-la-mujer-2024/ |
| CGPJ victim count (cross-check) | https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estadistica-por-temas/Datos-penales--civiles-y-laborales/Violencia-domestica-y-Violencia-de-genero/Victimas-mortales-de-violencia-de-genero-y-violencia-domestica-en-ambito-de-la-pareja-o-ex-pareja/ |

## Known annual counts (partner/ex-partner, confirmed)

**Source (2006–2026): `data/raw/feminicidios_delegacion_2003-2026.json`**, extracted
directly from each year's Delegación "ficha" PDF by `src/parsers/feminicide_parser.py`
(T19/T20; confidence=high, validation gate: sum(region) = total held exactly for all
21 years). **2003–2005 remain manually curated** (medium confidence) — those years use
a structurally different legacy PDF layout the parser does not extract (see T19 scope
note); if a future pass adds legacy-format extraction, replace these three rows too.

| Year | Count | Status |
|---|---|---|
| 2003 | 71 | First registry year — manually curated, legacy PDF format not parsed |
| 2004 | 72 | manually curated, legacy PDF format not parsed |
| 2005 | 57 | manually curated, legacy PDF format not parsed |
| 2006 | 69 | parsed, ficha updated 15 de octubre de 2025 |
| 2007 | 71 | parsed, ficha updated 15 de octubre de 2025 |
| 2008 | 76 | parsed, ficha updated 15 de octubre de 2025; highest on record |
| 2009 | 58 | parsed, ficha updated 15 de octubre de 2025 |
| 2010 | 74 | parsed, ficha updated 15 de octubre de 2025 |
| 2011 | 62 | parsed, ficha updated 15 de octubre de 2025 |
| 2012 | 51 | parsed, ficha updated 15 de octubre de 2025 |
| 2013 | 54 | parsed, ficha updated 15 de octubre de 2025 |
| 2014 | 57 | parsed, ficha updated 18 de diciembre de 2025 |
| 2015 | 59 | parsed, ficha updated 15 de octubre de 2025 |
| 2016 | 49 | parsed, ficha updated 15 de octubre de 2025 |
| 2017 | 49 | parsed, ficha updated 15 de octubre de 2025 |
| 2018 | 52 | parsed, ficha updated 15 de octubre de 2025 |
| 2019 | 56 | parsed, ficha updated 15 de octubre de 2025 |
| 2020 | 50 | parsed, ficha updated 23 de abril de 2026; COVID year |
| 2021 | 49 | parsed, ficha updated 23 de abril de 2026 |
| 2022 | 50 | parsed, ficha updated 23 de abril de 2026 |
| 2023 | 58 | parsed, ficha updated 23 de abril de 2026 |
| 2024 | 49 | parsed, ficha updated 23 de abril de 2026; 49% foreign-born |
| 2025 | 48 | parsed, ficha updated 23 de abril de 2026 |
| 2026 | 25 | parsed, ficha updated 29 de junio de 2026; **partial year, in progress** |
| Cumulative 2003–2026 | **1,366** | per 2026 ficha's own running total, see below |

**Why these differ from the previously published table here (2026-07-01 note):**
this doc's earlier table (written from secondary summaries, before the full-history
parser existed) reported 2024 as 47/51%-foreign and a 2003–2024 cumulative of 1,290.
The freshly parsed primary-source PDFs give 2024 = 49/49%-foreign and, more broadly,
differ from the old table in most years by 1–6 (e.g. 2018: 47 → 52; 2020: 44 → 50;
2021: 43 → 49). Root cause: **Delegación revises historical years retroactively** as
cases initially flagged "en investigación" are confirmed or reclassified — every ficha
PDF in `data/sources/` carries a recent `update_date` (Oct 2025 – Jun 2026), meaning
each row above is the *current, revised* figure as of that update, not the count as it
stood at the close of that calendar year. The parsed values are treated as more
authoritative (primary source, machine-extracted, validation-gated) and this table now
reflects them; the discrepancy itself is logged as SPEC.md §B22.

## Nationality breakdown 2024

- Spanish-born: 51.0% (25 of 49)
- Foreign-born: **49.0%** (24 of 49)
- Rate: Spanish women 1.68/million; foreign women 8.32/million → ratio **4.95×** (rate figure itself not re-derived this pass — carried over from the prior secondary source; population denominators may need revisiting given the updated victim counts)
- Cumulative foreign victims 2003–2026: see `origin` breakdown per year in the JSON; not re-summed here since 2003–2005 origin data is unavailable (legacy format)

## Caveats

- Registry began 2003; 2000–2002 requires INE series or police records
- Minor discrepancy between Delegación registry and CGPJ counts is expected in-year (cases under investigation at year-end); less relevant now that this doc tracks the ficha's own revised totals rather than a point-in-time snapshot
- Feminicidio.net broader count for 2024: 95 total female homicides (86 feminicidios) — different definition (see above), not directly comparable to this table
- 2026 row is a partial year (ficha dated 29 de junio de 2026) — will keep changing until the year closes
