# Source: Macroencuesta de Violencia contra la Mujer

**Publisher:** Ministerio de Igualdad / Delegación del Gobierno contra la Violencia de Género / INE  
**Type:** Large-scale victimisation survey; NOT police-reported crime data  
**Coverage:** Women 15+ resident in Spain; conducted irregularly  
**Waves:** 1999, 2002, 2006, 2011, 2015, 2019, 2024

## Access — 2024 wave (published 3 December 2025)

| Document | URL |
|---|---|
| Landing page | https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta-de-violencia-contra-la-mujer-2024/ |
| Executive summary (PDF) | https://violenciagenero.igualdad.gob.es/wp-content/uploads/Resumen-ejecutivo-MACROENCUESTA-2024.pdf |
| Full report (PDF) | https://violenciagenero.igualdad.gob.es/wp-content/uploads/Macroencuesta-2024.pdf |
| Methodological report | https://violenciagenero.igualdad.gob.es/wp-content/uploads/IMS_Macroencuesta-2024.pdf |
| La Moncloa press release | https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/igualdad/paginas/2025/031225-macroencuesta-violencia-genero.aspx |

## Access — 2019 wave

| Document | URL |
|---|---|
| Landing page | https://violenciagenero.igualdad.gob.es/violenciaEncifras/macroencuesta2015/Macroencuesta2019/home.htm |
| Full study (PDF) | https://violenciagenero.igualdad.gob.es/wp-content/uploads/Macroencuesta_2019_estudio_investigacion.pdf |
| Executive summary (PDF) | https://violenciagenero.igualdad.gob.es/wp-content/uploads/Resumen_ejecutivo_Macroencuesta_2019_DEF-1.pdf |
| Main results (PDF) | https://violenciagenero.igualdad.gob.es/wp-content/uploads/Principales_Resultados_Macroencuesta2019-1.pdf |

## Access — 2015 wave

| Document | URL |
|---|---|
| Landing page | https://violenciagenero.igualdad.gob.es/violenciaencifras/estudios/colecciones/libro-22-macroencuesta/ |
| Data tables | https://violenciagenero.igualdad.gob.es/macroencuesta2015/tablasviolencia/ |

## Access — all waves index

https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta/  
https://www.inmujeres.gob.es/MujerCifras/Violencia/Macroencuestas.htm

## Key figures

### 2024 wave (n=11,894; fieldwork Sept 2024–April 2025)
**⚠️ Methodology changed ("proceso estadístico de mejora") — NOT directly comparable to 2019.**

| Metric | Value | Definition |
|---|---|---|
| Sexual violence by partner (lifetime) | 7.7% | Women 15+ with partner history |
| Sexual violence outside partner (lifetime) | 14.5% | Women 16+ since age 15 |
| Rape, any perpetrator (lifetime) | **3.1%** | New module; no 2019 equivalent |
| Physical and/or sexual by partner (lifetime) | 12.7% | |
| Any violence (physical+sexual+econ+psych) by partner/ex (lifetime) | 30.3% | |
| Sexual harassment (acoso sexual), lifetime | 36.2% | |

### 2019 wave (n=9,568; population base 20,404,897 women 16+)

| Metric | Value | Absolute |
|---|---|---|
| Sexual violence outside partner (lifetime) | 13.7% | 2,802,914 women |
| Sexual violence by partner (lifetime) | 9.2% | 1,876,850 women |
| Rape outside partner (lifetime) | 2.2% | ~453,371 women |
| Physical and/or sexual by partner (lifetime) | 14.2% | ~2,897,896 women |
| Any machista violence, any perpetrator (lifetime) | 57.3% | 11,688,411 women |
| Sexual violence outside partner (last 12 months) | 1.8% | ~359,095 women |
| Reporting rate (denuncia) for sexual violence outside partner | 8% | 89–92% did NOT report |

### 2015 wave
| Metric | Value |
|---|---|
| Sexual violence outside partner (lifetime) | 12.5% |
| Sexual violence by partner (lifetime) | 8.4% |
| Physical and/or sexual by partner (lifetime) | 13.8% |

## Critical caveats

1. **Not comparable 2024 vs 2019**: The 2024 methodology improvement means some changes in prevalence figures may reflect measurement change, not real change.
2. **Survey vs police data**: Macroencuesta captures ACTUAL prevalence; police data captures REPORTED crimes. They cannot be compared as ratios to derive dark-figure multipliers without careful denominator alignment (avoid the "62× ratio" error — see SPEC B5).
3. **Annual prevalence (12-month reference)**: Only 2019 provides a clean 12-month estimate (1.8% for sexual violence outside partner). The 2024 wave should have a comparable figure — verify in full report.
4. **Definition comparability across waves**: Pre-2015 waves used different question wording; 2015 and 2019 are comparable to each other; 2024 is not fully comparable to 2019.

## Victim-perpetrator relationship (T98)

Both the 2019 and 2024 waves have a chapter dedicated to sexual violence **outside the couple/partner** ("violencia sexual fuera del ámbito de la pareja" — Cap. 16 in both editions) that asks victims directly who the aggressor was, unlike MIR's police-report table (`mir_informes_delitos_sexuales.md`) which can only record a relationship it identifies during the case. Full PDFs pulled into `data/sources/Macroencuesta_2019.pdf` / `Macroencuesta_2024.pdf`; verified figures hand-transcribed into `data/raw/macroencuesta_relationship_2015-2024.csv` (see that file's per-row `source_table`/`notes` columns for exact table/page citations — no automated PDF parser was built for this source this round, see note below).

**2019 wave** (N=620 women, lifetime, all severities pooled — the 2019 questionnaire couldn't ask relationship-to-perpetrator separately per severity tier, see report p.158): familiar 21.6%, amigo/conocido 50.5%, desconocido 39.1% (multiple response, sums >100%).

**2024 wave** is the first to break this down **by severity tier** (Tabla 16.20/16.21, p.268-270) — and the pattern is striking: the more severe the assault, the *less* likely the perpetrator is a stranger.

| Severity (2024, lifetime) | Familiar | Amigo/conocido | Desconocido |
|---|---|---|---|
| Violación (rape) | 23.1% | 62.7% | **12.0%** |
| Intento de violación (attempted rape) | 17.9% | 66.0% | 21.7% |
| Otras formas (non-penetrative touching etc.) | 18.6% | 48.5% | 46.5% |

The report's own framing: *"el 88% de las mujeres víctimas de una violación mencionan como agresor a un hombre que conocían de forma previa a la agresión"* (p.269) — i.e. only **12%** of rapes are by a stranger. The single largest specific category among rape perpetrators (31.6% on its own, Tabla 16.20) is a man with whom the victim had "a casual/sporadic affective-sexual relationship that never became a partnership" — a relationship type with no equivalent row in MIR's police table. The same known>stranger-with-severity gradient was already visible in the 2015 wave (quoted as a footnote in the 2019 report, p.158): desconocido was 18.8% for rape, 30.0% for attempted rape, 50.5% for non-penetrative touching — so this is a consistent finding across 3 waves (2015/2019/2024), not a one-off.

**Contrast with MIR's police-recorded table** (`mir_informes_delitos_sexuales.md`): once MIR's own relationship data is restricted the same way (partner-excluded, renormalized over its 3 non-pareja groups — `_survey_comparison()` in `src/sexual_crimes/build_dashboard_data.py`), MIR's 2024 "unknown" share is **78.5%** — 6-7x the survey's rape-specific 12.0%, and still nearly double the survey's lowest-severity 46.5%. This is the expected direction (police records structurally undercount known-perpetrator assaults, since victims report those at far lower rates — see the GEAV/MIR 2020 synthesis's 90.1% non-report rate outside partner vs. 88.7% within partner, cited in `mir_informes_delitos_sexuales.md`), but the *size* of the gap is itself a finding: most of what MIR's "unknown" bucket actually represents is not stranger assault, but assault where the police never determined (or the case was never resolved enough to record) the relationship — folding in an unknown mix of real strangers and unresolved-but-known cases. Visualized directly in the dashboard's `sx-relationship-survey` panel.

**Not yet done**: no automated parser for the Macroencuesta series exists (the CSV above is hand-curated from 2 waves). Given the survey is irregular (waves roughly every 4-5 years: 1999/2002/2006/2011/2015/2019/2024) the ROI on a full PDF-table parser is much lower than for MIR's annual series — a future wave could just be hand-added to the same CSV. If a parser is ever built, `parse_relationship_rows`-style line-regex against `page.extract_text()` (the approach that worked well for MIR's own relación table, `mir_parser.py`) is a reasonable starting point, since Tabla 16.20/16.21 print as clean text in both waves checked.
