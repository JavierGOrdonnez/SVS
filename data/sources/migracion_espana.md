# Source: Spain Immigration / Migration Data — INE + Eurostat + MISSM

**Used for:** §T11 (covariate series — total immigration flow & stock by year, nationality, sex, age) per SPEC.md.

---

## 1. INE — Estadística de Migraciones y Cambios de Residencia (EMCR)

**Publisher:** Instituto Nacional de Estadística (INE)
**Coverage:** Annual international and internal migration flows, by sex, 5-yr age group, country of origin/destination, nationality (Spanish/foreign), country of birth.
**Series start:** 2008 (replaces the prior EVR for international flows).
**Methodology:** Statistical estimate that reconciles Padrón inscriptions/cancellations with population register adjustments; comparable across years from 2008.

| Resource | URL |
|---|---|
| Main operation page | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177000&menu=ultiDatos&idp=1254735573002 |
| Latest data hub (EMCR) | https://www.ine.es/uc/SwecU4nGi1 |
| EMCR 2024 press release | https://www.ine.es/dyngs/Prensa/EMCR2024.htm |
| Table 24290 — flow by year, sex, age, country of origin, nationality, country of birth | https://www.ine.es/jaxiT3/Tabla.htm?t=24290&L=0 |
| Table 24293 — flow by year, nationality, country of birth | https://www.ine.es/jaxiT3/Tabla.htm?t=24293&L=0 |
| Table 24295 — flow by year, country of origin, nationality | https://www.ine.es/jaxiT3/Tabla.htm?t=24295&L=0 |
| Table 24312 — flow by CCAA, year, sex, age, nationality | https://www.ine.es/jaxiT3/Tabla.htm?t=24312&L=0 |
| Table 24322 — flow by province, year, sex, age, nationality | https://www.ine.es/jaxiT3/Tabla.htm?t=24322&L=0 |
| Table 24328 — net migration with abroad by province, year, sex, age, nationality | https://www.ine.es/jaxiT3/Tabla.htm?t=24328 |

---

## 2. INE — Estadística de Variaciones Residenciales (EVR) [historical]

**Coverage:** Annual residential variations 1998–2020; for international flows, superseded by EMCR from 2008 onwards but remains the canonical source for 2000–2007.
**Methodology change flags:** 2004 (inclusion of altas por omisión & bajas por inscripción indebida); 2006 (inclusion of bajas por caducidad for non-EU foreigners). These breaks ! flagged in `notes` per SPEC V7-analogue.

| Resource | URL |
|---|---|
| EVR methodology note | https://www.ine.es/daco/daco42/migracion/notaevr.htm |
| EVR metadata | https://www.ine.es/dynt3/metadatos/es/RespuestaPrint.html?oper=202 |
| EVR altas por sex/edad (historical px files) | https://www.ine.es/jaxi/Tabla.htm?path=/t20/p307/a2011/l0/&file=020521.px |

---

## 3. INE — Padrón Continuo / Estadística Continua de Población (ECP)

**Used for:** Stock of foreign-nationality and foreign-born population at 1 January each year, 2000–2025.
**Publisher:** INE.
**Methodology change:** Padrón Municipal Continuo until end-2020; replaced by ECP (Estadística Continua de Población) from 2021Q1, which adds methodological harmonisation and quarterly reference dates.

| Resource | URL |
|---|---|
| Padrón main operation page | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177012&menu=ultiDatos&idp=1254734710990 |
| ECP 1 Jan 2025 press release | https://www.ine.es/dyngs/Prensa/ECP4T24.htm |
| ECP 1 Jan 2026 (prov.) press release | https://www.ine.es/dyngs/Prensa/ECP4T25.htm |
| Table 36825 — foreign pop by country of nationality, 5-yr age, sex | https://www.ine.es/jaxiT3/Tabla.htm?t=36825&L=0 |
| Table 02005 — foreign pop by nationality, CCAA, sex, year | https://www.ine.es/jaxi/Tabla.htm?path=%2Ft20%2Fe245%2Fp08%2Fl0%2F&file=02005.px&L=0 |
| Table 68535 — population by sex, 5-yr age, nationality (ES/foreign) | https://www.ine.es/jaxiT3/Tabla.htm?t=68535 |
| Table 31304 — population by sex, age, nationality | https://www.ine.es/jaxiT3/Tabla.htm?t=31304&L=0 |

---

## 4. Eurostat — Cross-check for 2008–2024 flows

**Publisher:** Eurostat, harmonised under EU Reg. 862/2007 + 2020 amendment.

| Resource | URL |
|---|---|
| migr_imm1ctz — Immigration by age group, sex, citizenship | https://ec.europa.eu/eurostat/databrowser/view/migr_imm1ctz/default/table?lang=en |
| migr_imm2ctz — Immigration by age, sex, group of citizenship | https://ec.europa.eu/eurostat/databrowser/view/migr_imm2ctz/default/table?lang=en |
| migr_pop1ctz — Population by citizenship & country of birth (1 Jan stock) | https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table?lang=en |

---

## 5. MISSM / OPI — Foreign workers by occupation/sector

**Publisher:** Ministerio de Inclusión, Seguridad Social y Migraciones — Observatorio Permanente de la Inmigración.
**Used for:** "Occupation" dimension. INE migration statistics do NOT publish a by-occupation breakdown of immigrants; the closest official series is the stock of foreign workers affiliated to Spanish Social Security by Régimen (sector).

| Resource | URL |
|---|---|
| OPI main statistics catalogue | https://www.inclusion.gob.es/web/opi/estadisticas |
| Afiliación de extranjeros a la Seguridad Social (by Régimen) | https://www.inclusion.gob.es/web/opi/estadisticas/catalogo/afiliacion |
| Stock — Personas extranjeras con autorización de residencia en vigor | https://www.inclusion.gob.es/en/web/opi/estadisticas/catalogo/stock_documentacion |

**Régimen categories:** General (incl. sub-systems Agrario & Hogar from 2012), Autónomos, Mar, Minería del Carbón. These act as a proxy for sector of employment.

---

## 6. Definition glossary

| Term | Definition used |
|---|---|
| **Intake / flow / immigration** | Persons arriving in Spain from abroad during the calendar year. EMCR variable: *inmigración procedente del extranjero*. Includes both Spanish nationals returning and foreign nationals. |
| **Stock — foreign nationality** | Persons resident in Spain at 1 January whose nationality is non-Spanish. INE/ECP "población extranjera". |
| **Stock — foreign born** | Persons resident in Spain at 1 January born outside Spain (regardless of current nationality). INE/ECP "población nacida en el extranjero". |
| **Net migration balance** | Immigrations from abroad − emigrations to abroad in the year. |

---

## 7. Known data caveats

- **Break 2008:** Series source changes from EVR → EMCR. Pre-2008 figures use EVR methodology; not strictly comparable to 2008+ but published by INE on a continuous basis.
- **Break 2021:** Padrón → ECP. Stock numbers from 1 Jan 2021 onwards use ECP, which introduced harmonisation adjustments that produced step-changes vs Padrón.
- **Brexit (2020-01):** UK citizens reclassified from EU to non-EU in INE flow tables.
- **"Country of origin" ≠ "country of nationality" ≠ "country of birth"** — three different variables in the same table. Use the right one for your question.
- **No "occupation" breakdown** in primary migration statistics. Use MISSM affiliation data as a proxy; note that affiliation captures only persons with Social Security coverage, missing informal sector and short-stay arrivals.
