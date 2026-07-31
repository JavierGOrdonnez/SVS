# Source: INE — Population (Padrón) & Condenados & Femicide Series

**Publisher:** Instituto Nacional de Estadística (INE)

---

## 1. Padrón Municipal Continuo — Female Population by Age

**Used for:** denominators in incidence-rate calculations

| Resource | URL |
|---|---|
| Main operation page | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177012&menu=resultados&secc=1254736195461&idp=1254734710990 |
| Population by sex, age, nationality (table 31304) | https://www.ine.es/jaxiT3/Tabla.htm?t=31304&L=0 |
| Population by sex, municipality (table 33844) | https://www.ine.es/jaxiT3/Tabla.htm?t=33844&L=0 |
| Cifras de Población (mid-year estimates) | https://www.ine.es/uc/pFdjFZnPi1 |

Padrón series starts 1996; annual at 1 January each year.

---

## 1b. INE table 56936 — direct Spanish/foreign nationality split (T89, fixes B44)

**Used for:** Spanish-national population, wherever a Spanish/foreign population
denominator split is needed repo-wide (migration dashboard's Spain line +
Spanish age pyramid, peligrosidad, feminicide rates, general crime trends,
cohort crime rate). Table 31304 above was originally flagged as the intended
source for this but never actually built against; table 56936 was chosen
instead because it's the *same ECP product family* as table 56934 (already
used for total population, `parse_ine_population.py`) — same quarterly
cadence, same July-1 midyear reference date — so pairing them needs no
date-alignment guesswork.

| Resource | URL |
|---|---|
| Table 56936 (browser UI) | https://www.ine.es/jaxiT3/Tabla.htm?t=56936 |
| CSV download | https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/56936.csv?nocab=1 |

Coverage: 2002–2025 (quarterly; some quarters suppressed pre-2021, same
pattern as t.56934). `Nacionalidad` column reports `Española`/`Extranjera`/
`Total` directly, cross-tabbed with sex and 5-year age bands. Parsed by
`src/analysis/parse_ine_population_nationality.py` → `data/processed/
population_spain_nationality.csv` (July-1 rows only, 2002+, per V46).

### Why this replaced a derived subtraction (B44)

Every consumer of "Spanish-national population" in this repo used to
compute `total_population(t.56934) − foreign_stock(Eurostat migr_pop1ctz,
top ~50 nationalities)`. That mixed a July-1 total with a January-1 foreign
figure covering a shifting ~86–94% of foreign residents — the uncounted
foreign residents got misattributed into "Spain," producing a
non-constant, spurious wiggle. Comparing the two series directly:

| Year | Derived (total − Eurostat foreign) | Primary (t.56936 "Española") | Gap |
|---|---|---|---|
| 2002 | 39,754,683 | 39,364,640 | +390,043 |
| 2005 | 40,351,859 | 39,950,570 | +401,289 |
| 2008 | 41,063,808 | 40,717,715 | +346,093 |
| 2010 | 41,339,579 | 41,208,701 | +130,878 |
| 2013 | 41,696,486 | 41,718,434 | −21,948 |
| 2016 | 42,187,184 | 42,041,287 | +145,897 |
| 2019 | 42,457,538 | 42,054,137 | +403,401 |
| 2020 | 42,349,026 | 41,999,670 | +349,356 |
| 2021 | 42,203,084 | 41,978,121 | +224,963 |
| 2022 | 42,542,830 | 41,994,341 | +548,489 |
| 2023 | 42,533,747 | 42,034,958 | +498,789 |
| 2024 | 42,645,149 | 42,169,185 | +475,964 |

The gap swings from −22K to +548K with no stable pattern — an artifact of
the method, not of real Spanish demography. The real (t.56936) series is
materially smoother year-to-year than the derived one. See `SPEC.md` §B44
and §V46.

---

## 2. Estadística de Condenados — Adult & Minor Offenders

**Used for:** conviction counts by crime type, sex, nationality

| Year | Press release HTML | Press release PDF |
|---|---|---|
| 2024 | https://www.ine.es/dyngs/Prensa/ECAECM2024.htm | https://www.ine.es/dyngs/Prensa/ECAECM2024.pdf |
| 2023 | https://www.ine.es/dyngs/Prensa/es/ECAECM2023.htm | — |
| Series main page | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=estadistica_C&cid=1254736177001&menu=ultiDatos&idp=1254735573206 | — |
| INE table 28857 (condenados delitos sexuales) | https://www.ine.es/jaxi/Tabla.htm?t=28857 | — |
| INE table 28715 (delitos sexuales por edad) | https://www.ine.es/jaxi/Tabla.htm?t=28715 | — |
| INE table 28716 (delitos sexuales por nacionalidad) | https://www.ine.es/jaxi/Tabla.htm?t=28716 | — |

### Confirmed 2024 figures (published 18 September 2025)

**Adults:** 5,230 delitos (+50.8% vs 2023) by 5,230 convicted persons (+37.3%)
- Abuso y agresión sexual menores <16: 1,151
- Abuso sexual: 1,097
- Agresión sexual: 1,389 (of which **90 = violación**)
- Otros: 1,593
- Sum check: 1,151+1,097+1,389+1,593 = **5,230 ✓**
- Note: 90 violaciones is a **subcategory** of 1,389 agresiones, NOT additive

**Minors:** 825 delitos (+65.0%) by 550 convicted minors (+29.7%)
- Abuso y agresión sexual menores <16: 383
- Abuso sexual: 72
- Agresión sexual: 119 (of which **9 = violación**)
- Otros: 251
- Sum check: 383+72+119+251 = **825 ✓**
- 95.6% male

**Adults 2023:** 3,468 delitos (−9.6% vs 2022)  
**Minors 2023:** 500 delitos (−21.4% vs 2022) by ~500 minors

---

## 3. Femicide Series — Víctimas Mortales 1999–present

| Resource | URL |
|---|---|
| INE table v02001.px (series 1999–2025) | https://www.ine.es/jaxi/Tabla.htm?path=%2Ft00%2Fmujeres_hombres%2Ftablas_1%2Fl0%2F&file=v02001.px&L=0 |
| INE table v02006.px (by CCAA, 2025) | https://www.ine.es/jaxi/Tabla.htm?path=%2Ft00%2Fmujeres_hombres%2Ftablas_1%2Fl0%2F&file=v02006.px&L=0 |
| INE EVDVG 2024 press release | https://www.ine.es/dyngs/Prensa/EVDVG2024.htm |

This series is the primary source for 2000–2002 femicide counts (pre-Delegación registry).

---

## 4. Estadística de Violencia Doméstica y de Género (EVDVG)

**Used for:** denuncias, protection orders, judicial outcomes (different from police denuncias in CGPJ)

| Resource | URL |
|---|---|
| 2024 press release | https://www.ine.es/dyngs/Prensa/EVDVG2024.htm |
| Main operation | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176866&menu=ultiDatos&idp=1254735573206 |
