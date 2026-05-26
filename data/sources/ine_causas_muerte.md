# Source: INE — Defunciones según la Causa de Muerte (ECM)

Annual cause-of-death microdata for Spain, broken down by sex × age group × cause (ICD-10 reduced list).

---

## Coverage

| Dimension | Values |
|---|---|
| Years | 1980–2024 (we pull 2000–2024 = 25 years; 2025 not yet published) |
| Sex | `all` (Ambos sexos), `male` (Hombres), `female` (Mujeres) |
| Age groups | 22: `<1`, `1-4`, `5-9`, `10-14`, …, `90-94`, `95+`, plus `all` (Todas las edades) |
| Causes | 120 entries in INE "lista reducida" — 17 chapter aggregates (I, II, III, IV, V, VI-VIII, IX, X, XI, XII, XIII, XIV, XV, XVI, XVII, XVIII, XX), 1 grand total (I-XXII), 102 specific causes |
| Unit | Deaths in calendar year (Personas) |
| Geography | Total Nacional |

Total cell count: 3 × 22 × 120 × 25 = 198,000 data points.

## Source URLs

| Resource | URL |
|---|---|
| INEbase operation page | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176780 |
| Table 7947 (browser UI) | https://www.ine.es/jaxiT3/Tabla.htm?t=7947 |
| JSON API — all data | https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/7947?tip=A |
| JSON API — last N years | https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/7947?nult=N&tip=A |
| Press release 2023 | https://www.ine.es/dyngs/Prensa/pEDCM2023.htm |
| API documentation | https://www.ine.es/dyngs/DAB/index.htm?cid=1102 |

## How we pulled the data

```
curl -s "https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/7947?nult=25&tip=A" \
  -o /tmp/ine_mortality_full.json     # ~24 MB JSON, 7,920 series × 25 years
python3 src/parse_ine_mortality.py /tmp/ine_mortality_full.json \
  data/processed/mortality_spain_ine_ecm.csv
python3 src/summarize_mortality.py data/processed/mortality_spain_ine_ecm.csv
```

Pulled 2026-05-20. All 2024 figures marked `Definitivo` (final) by INE.

## Output files

| File | Rows | Description |
|---|---|---|
| `data/processed/mortality_spain_ine_ecm.csv` | 198,001 | Full tidy data: year × sex × age × cause × deaths |
| `data/processed/mortality_by_chapter.csv` | 1,275 | year × sex × chapter (all-age aggregate) |
| `data/processed/mortality_by_age_sex.csv` | 1,650 | year × sex × age (all-cause aggregate) |
| `data/processed/mortality_key_causes.csv` | 11,550 | year × sex × age × {all-cause, homicide, suicide, traffic, drug poisoning, undetermined intent} |

## Schema — `mortality_spain_ine_ecm.csv`

| Column | Type | Example | Notes |
|---|---|---|---|
| `year` | int | 2024 | Calendar year of death |
| `sex` | enum | `female` | `all` ∣ `male` ∣ `female` |
| `age_group` | enum | `15-19` | 22 groups; `all` = Todas las edades |
| `cause_chapter` | str | `II` | ICD-10 chapter label when applicable; empty for sub-causes; `I-XXII` = grand total |
| `cause` | str | `Tumor maligno de la mama` | INE "lista reducida" cause name |
| `deaths` | int | 6562 | Count |
| `data_type` | enum | `Definitivo` | `Provisional` ∣ `Definitivo` (final) |
| `series_cod` | str | `ECM351` | INE Tempus3 series identifier |

## ICD-10 chapter map (INE reduced list)

| Label | Chapter |
|---|---|
| I | Enfermedades infecciosas y parasitarias |
| II | Tumores |
| III | Enfermedades de la sangre y trastornos inmunitarios |
| IV | Enfermedades endocrinas, nutricionales y metabólicas |
| V | Trastornos mentales y del comportamiento |
| VI-VIII | Sistema nervioso + ojo + oído (combined) |
| IX | Sistema circulatorio (heart disease, stroke) |
| X | Sistema respiratorio |
| XI | Sistema digestivo |
| XII | Piel y tejido subcutáneo |
| XIII | Sistema osteomuscular |
| XIV | Sistema genitourinario |
| XV | Embarazo, parto y puerperio |
| XVI | Afecciones originadas en el periodo perinatal |
| XVII | Malformaciones congénitas |
| XVIII | Síntomas y signos no clasificados |
| XX | Causas externas (XX in INE = ICD-10 XX "Causas externas de mortalidad"; includes accidents, suicide, homicide, undetermined intent) |
| I-XXII | All-cause total |

Note: ICD-10 chapters XIX (injury/poisoning consequences) and XXI–XXII are not used as separate aggregates in INE's reduced list — XX is the only external-causes chapter.

## Caveats

- **Year of registration ≠ year of event.** A homicide in late December may appear in the next year if death follows later. INE counts by calendar year of death.
- **Provisional vs definitive.** Press releases use provisional figures (~6 months after year-end); definitive data published ~18 months after year-end. Our pull (2026-05) shows 2024 as definitive.
- **MIR police count differs.** MIR Balance de Criminalidad counts police-registered homicide incidents (348 in 2023). INE ECM counts deaths certified by medical/judicial cause (316 in 2023). Gap arises from unresolved/pending classifications. Use INE for cause-of-death analysis, MIR for criminal-justice context.
- **Underlying cause only.** INE assigns one underlying cause per death; multi-morbidity not captured.
- **Suicide undercount.** "Eventos de intención no determinada" (undetermined intent) is a known suicide proxy — partial undercount exists when coroner cannot rule suicide definitively.
- **Definition changes.** ICD-10 has been used since 1999; no major break in 2000–2024 window. INE reduced-list categories have remained stable, but a few series were renamed (e.g. COVID-19 added 2020).

## Cross-checks performed

| Metric | INE pulled | Source-doc expected | Match? |
|---|---|---|---|
| 2020 all-cause total | 493,776 | "COVID spike year" | ✓ (vs ~422k normal years) |
| 2023 homicide total | 316 | ~300 (provisional press) | ✓ (definitive > provisional) |
| 2023 female homicide | 99 | ~96 (provisional) | ✓ |
| 2023 male homicide | 217 | ~204 (provisional) | ✓ |
| 2000–2024 series count | 7,920 (= 3×22×120) | matches dimension product | ✓ |
