# Q&A note — sexual-crime reporting vs. convictions, recidivism, and foreign-offender expulsion (Spain)

**Type:** Research conversation log, not a primary data source. Captures questions asked, answers given,
and every reference/link surfaced while answering. Treat external news-outlet figures here as
**unverified** until cross-checked against the primary tables already in this repo
(`mir_informes_delitos_sexuales.md`, `cgpj_violencia_genero.md`, `fiscalia_memorias.md`,
`ine_poblacion_femicidios.md`) — see caveats inline.

---

## Q1. Is the ~20,000 MIR sexual-aggression figure *reported* crimes, or *confirmed* (judicially convicted) aggressors?

**Answer:** Reported/recorded crimes — not convictions. Several different "~20k" numbers circulate and get
conflated; they sit at different stages of the funnel:

| Stage | 2024 figure | Source |
|---|---|---|
| Crimes recorded by police (denuncias) | **22,846** total sexual offenses (~5,223 rapes w/ penetration + ~13,673 without) | MIR *Informe sobre Delitos contra la Libertad Sexual 2024* — see `mir_informes_delitos_sexuales.md` |
| Suspects detained/investigated | 14,375 (93% male) — still just suspects, presumption of innocence applies | same MIR report |
| Preliminary proceedings opened (diligencias previas) | 20,711 (+12% vs 2023) | Fiscalía General del Estado, Memoria 2024 — see `fiscalia_memorias.md` |
| Adults actually convicted (sentencia firme) | **~5,230** (one source) / **3,936** (another INE/MIR cross-check, +37.3% vs prior year) — figures not yet reconciled | CGPJ/INE "Condenados" registry, 2024 — see `ine_poblacion_femicidios.md` |

Whichever "~20,000" is being cited in public debate, it is almost certainly the police- or
prosecution-stage count, not convicted offenders. The gap between ~20k reported and ~4–5k convicted
reflects cases dropped at instruction, acquittals, and **time lag** (a 2024 conviction often stems from
a complaint filed years earlier) — it is *not* a same-cohort conviction rate, and dividing one by the
other would be methodologically invalid (same error flagged for other ratios in this repo's early,
Haiku-generated pass, which fabricated several stage-mismatched ratios; that critique doc was removed
as superseded by §B once its findings were folded into SPEC.md — see git history pre-2026-07 for the
original writeup).

Separately, survey data (Macroencuesta) suggests only ~16–33% of sexual-violence victims report at
all, so true incidence is a further multiple above the reported figures — a distinct "dark figure"
question from reported-vs-convicted.

**This repo currently lacks:** a longitudinal cohort-based conviction-rate computation (tracking the
same complaints through to outcome). The CGPJ "Condenados" registry has a reincidencia field, flagged
pending extraction in the now-removed `data/haiku_artifacts/` notes (see git history pre-2026-07 for
the original writeup) — still an open gap, not yet re-tracked in `SPEC.md` §T.

---

## Q2. Is there evidentiary substrate for "rape carries high reincidence → should justify lifelong sentences"?

**Answer:** Mixed. Supports concern for a *subgroup*, not a blanket claim.

**Spain-specific:**
- Redondo et al., 3.8-year follow-up of 123 sex offenders released 1991–2002: **32.2%** any
  reoffense, **19.8%** new sexual offense.
- Catalonia's CERCLES program (community supervision for high-risk released offenders): ~90% of
  treated offenders do not return to the penal system (~10% recidivism in that managed cohort).
- Secretaría General de Instituciones Penitenciarias cohort study (releases 2009–2019): sex offenders
  have one of the **lowest** recidivism rates of all offense categories, roughly **~20%**, comparable
  to or below the general prison-population average — "8 of 10 sex offenders do not reoffend."

**International meta-analyses (larger samples, standard reference point):**
- Hanson & Bussière (1998): n=28,972, **13.4%** sexual recidivism, ~4–5 yr follow-up.
- Hanson & Morton-Bourgon (2004): n=31,216, **13.7%** sexual-specific / **36.9%** *any* recidivism,
  ~5–6 yr follow-up.
- Longer horizons: ~5–15% sexual recidivism at 5 years, ~10–20% at 10 years.
- Hanson, Harris, Helmus & Thornton (2014): even *high-risk* offenders' 5-yr sexual-recidivism risk
  drops from 22% (at release) to ~4.2% after 10 offense-free years in the community — risk decays
  with time, it is not flat.

**Conclusion used in the conversation:** "high reincidence" is well-supported for *general*
reoffending (~36%) but the sexual-specific reoffense rate (13–20%) is lower than common perception,
and concentrated in a high-risk subgroup rather than evenly distributed — which argues for
risk-differentiated supervision (already partly implemented, see Q3) rather than a uniform lifelong
sentence applied to the whole "rape" category irrespective of risk profile.

---

## Q3. How is "high-risk" determined, and do rates differ by offense type (rape vs. other sexual aggression)?

**Risk determination:** structured actuarial instruments, principally **Static-99R** (+ Static-2002R),
scored on static/historical factors: age at release, never having lived with a partner 2+ years,
non-sexual violence in the index offense, number of prior sexual/non-sexual convictions, unrelated or
stranger victims, any male victims, number of prior sentencing occasions. Dynamic factors (Stable-2007,
Acute-2007, VRS-SO) — deviant sexual interest, hostility to women, poor self-regulation, supervision
non-compliance — are layered on top and explain why risk can rise or fall with behavior in the
community.

**Recidivism by offense type** (meta-analytic ranges):

| Offense type | Sexual recidivism range | Notes |
|---|---|---|
| Incest offenders (familial) | ~4–10% | Lowest risk group consistently |
| Child molesters, female victims | ~10–29% | |
| Rapists (adult victims, force/penetration) | ~7–35%, pooled estimate ~18.9% | Higher non-sexual violent recidivism too |
| Child molesters, male victims | ~13–40% | Higher than female-victim molesters |
| Exhibitionists / non-contact | ~41–71% | Highest *repeat* rate but lowest per-incident severity — different harm profile, not a rape-escalation indicator |

Key nuance: "recidivism" in these studies means *any* new sex-crime conviction, not necessarily the
same offense type as the index crime. Rapists show higher general violent recidivism (broader
criminality pattern); intrafamilial child abuse is more often a specialized, lower-general-criminality
pattern. Stranger/unrelated-victim status predicts recidivism better than the legal offense category
itself.

---

## Q4. How is sex-offender risk management actually implemented in Spain?

- **During sentence:** prison treatment program (*Programa de Control de la Agresión Sexual*, PCAS),
  cognitive-behavioral, with periodic risk reassessment.
- **At release:** *libertad vigilada* (supervised release) is **mandatory** for sex offenders given a
  prison sentence, for **5–10 years post-sentence** (exception: first-time, single-offense, primary
  offenders). Conditions can include check-ins, GPS, exclusion zones, treatment mandates, professional
  bans involving minors.
- **Registro Central de Delincuentes Sexuales** (2015/2016) — enables background checks for jobs
  involving contact with minors.
- **CERCLES** (Catalonia) — Circles of Support and Accountability for high-risk released offenders;
  reports very low re-offense among participants.
- **Prisión permanente revisable** (LO 1/2015) for the most extreme cases (murder of a minor with
  sexual aggravation, etc.) — reviewable only after 25–35 years.
- **Outcome data:** Instituciones Penitenciarias cohort study above (~20% recidivism, among the lowest
  categories) — undercuts the "irredeemable" framing used in some lifelong-sentence arguments.

---

## Q5. What actually happens when a foreign national commits a serious crime in Spain (esp. sexual)?

Two distinct legal mechanisms are routinely conflated in public debate — separated here:

**(a) Pretrial detention (prisión provisional) — nationality is not the deciding factor.**
Art. 503 LECrim sets identical rules for everyone: requires risk of flight, evidence destruction, or
reoffense risk (habitual/organized crime), and the alleged crime's maximum penalty must be ≥2 years (or
lower with prior convictions). Rape/sexual aggression with penetration (6–12 years) easily clears this
bar, so pretrial detention is legally available regardless of nationality. Viral "released pending
trial" cases involve judicial discretion on the specific facts (flight/reoffense risk not sufficiently
evidenced), not an immigration-status carve-out — and occur for Spanish and foreign suspects alike. A
documented example: a man in Granada (June 2026) held in *prisión provisional* for sexual assault, with
prior convictions for similar facts — the mechanism for flagging/detaining repeat offenders exists and
is used.

**(b) Expulsion as substitute for prison (Art. 89 CP) — mostly does not apply to rape.**
- Sentences **1–5 years**: a judge *may* substitute prison with expulsion + 5–10 year re-entry ban.
  This can apply to some lower-bracket sexual-abuse-without-penetration convictions.
- Sentences **≥5 years** — the bracket *violación* (rape with penetration) typically falls into
  (6–12 years) — **the law requires the sentence (or part of it) to be served in Spain first.**
  Expulsion can only be applied to whatever portion remains once the person reaches parole eligibility
  /tercer grado, substituting the remainder. By design, immediate "convicted then expelled" is excluded
  for crimes of this severity.
- EU citizens: expulsion permitted only if they represent a threat to public order/security, applied
  restrictively.
- Spain has expelled 140,000+ people total since record-keeping began, but this is dominated by
  administrative/irregular-status expulsions, not sentence-substitution for serious crime — no verified
  breakdown isolating sex-crime-specific expulsions was found.

**On the "migrants reoffend more" claim specifically:** a circulating figure (foreigners ~7.9% sexual
recidivism vs. Spaniards ~24.8%) would run *opposite* to the headline claim, but could not be traced to
a verifiable primary government table in this session — **treat as unverified, not as fact**. What is
better supported is that the commonly cited "foreigners commit sexual crimes at ~5× their population
share" statistic answers a different question (overrepresentation in first-time offending, confounded
by age/sex structure of migrant populations and differential police contact) than recidivism
(whether someone already convicted once reoffends more after release). Conflating the two converts a
population-composition fact into an unsupported recidivism claim. Given this repo's documented history
of confabulated statistics on this exact topic (see git history pre-2026-07 for the removed
Haiku-artifacts critique, folded into SPEC.md §B), any specific
nationality-recidivism percentage should be verified against an INE/Instituciones
Penitenciarias/CGPJ primary table — including table 28716 (`ine_poblacion_femicidios.md`) — before use
in either direction of the argument.

---

## All references / links surfaced in this conversation

**Official / primary sources:**
- [MIR — Informe sobre delitos contra la libertad e indemnidad sexual en España (index, all years)](https://www.interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/informe-sobre-delitos-contra-la-libertad-e-indemnidad-sexual-en-espana/)
- [MIR — Informe sobre delitos contra la libertad sexual. España 2024 (PDF)](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf)
- [ONVIOS — Informe anual sobre delitos contra la libertad sexual 2024](https://onvios.ses.mir.es/publico/onvios/dam/jcr:76301b08-9d21-4752-ba4c-ed5998b56134/Informe_DelitosSexuales%202024.pdf)
- [INE — Nota de prensa: Estadística de Condenados Adultos/Menores 2024](https://www.ine.es/dyngs/Prensa/ECAECM2024.htm) / [PDF](https://www.ine.es/dyngs/Prensa/ECAECM2024.pdf)
- [INE — Tabla 28752: Delitos sexuales según nacionalidad](https://www.ine.es/jaxiT3/Tabla.htm?t=28752)
- [Ministerio del Interior — Avance estudio de reincidencia (Secretaría General de Instituciones Penitenciarias)](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/noticias/documentos/2022/09_Septiembre/Avance_estudio_reincidencia-.pdf)
- [CGPJ — El TS establece que no se puede sustituir pena de prisión inferior a un año impuesta a extranjero por expulsión](https://www.poderjudicial.es/cgpj/es/Poder-Judicial/Noticias-Judiciales/El-Tribunal-Supremo-establece-que-no-se-puede-sustituir-una-pena-de-prision-inferior-a-un-ano-impuesta-a-un-ciudadano-extranjero-por-una-de-expulsion)
- [BOE — Doctrina de la Fiscalía General del Estado (expulsión de extranjeros)](https://www.boe.es/buscar/abrir_fiscalia.php?id=FIS-C-2015-00007.pdf)

**Academic / risk-assessment literature:**
- [Hanson & Bussière (1998) — Predicting relapse: a meta-analysis of sexual offender recidivism studies (PubMed)](https://pubmed.ncbi.nlm.nih.gov/9583338/)
- [Hanson, Harris, Helmus & Thornton (2014) — High-Risk Sex Offenders May Not Be High Risk Forever](https://journals.sagepub.com/doi/abs/10.1177/0886260514526062) / [PubMed summary](https://pubmed.ncbi.nlm.nih.gov/24664250/)
- [Hanson, Lee & Thornton (2024) — Long Term Recidivism Rates Among Individuals at High Risk to Sexually Reoffend](https://journals.sagepub.com/doi/10.1177/10790632221139166)
- [Lussier, McCuish, St-Pierre & Baguet (2025) — Examining Benchmarks of Sexual Recidivism Rates for Short/Moderate/Long-Term Follow-Up](https://journals.sagepub.com/doi/10.1177/15248380251338791)
- [Longitudinal Patterns of Sexual Recidivism by Age Over a 25-Year Follow-Up in California (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11778740/)
- [The Characteristics of Persistent Sexual Offenders: A Meta-Analysis of Recidivism Studies (ICMEC PDF)](https://www.icmec.org/wp-content/uploads/2015/10/Characteristics-of-Persistent-Sex-Offenders-Meta-Analysis-of-Recidivism-2005.pdf)
- [Song & Lieb — Adult Sex Offender Recidivism: A Review of Studies (WSIPP PDF)](https://www.wsipp.wa.gov/ReportFile/1161/Wsipp_Adult-Sex-Offender-Recidivism-A-Review-of-Studies_Full-Report.pdf)
- [SMART/OJP — Chapter 5: Adult Sex Offender Recidivism](https://smart.ojp.gov/somapi/chapter-5-adult-sex-offender-recidivism)
- [SMART/OJP — Chapter 6: Sex Offender Risk Assessment](https://smart.ojp.gov/somapi/chapter-6-sex-offender-risk-assessment)
- [CDCR — STATIC-99R overview (PDF)](https://www.cdcr.ca.gov/bph/wp-content/uploads/sites/161/2021/04/Apr2021_CBI-SO-_Risk_Assessments_Information.pdf)
- [Oregon BOPPPS — Static-99R & Static-2002R Evaluators' Workbook (PDF)](https://www.oregon.gov/boppps/Documents/R&R/Static%20Evaluators_Workbook_2021-09-28.pdf)
- [El riesgo de reincidencia en agresores sexuales (Redalyc PDF)](https://www.redalyc.org/pdf/778/77828305.pdf)
- [Redondo Illescas — Revista Española de Investigación Criminológica (Dialnet PDF)](https://dialnet.unirioja.es/descarga/articulo/2477656.pdf)
- [La reincidencia sexual: breve resumen del estado de la cuestión — POSTC. Crimen, Ciencia, Sociedad (UMH)](https://postc.umh.es/minipapers/la-reincidencia-sexual-breve-resumen-del-estado-de-la-cuestion/)

**Programs / secondary reporting (context, not primary data):**
- [Fundación Salud y Comunidad — Nueve de cada diez condenados por delitos sexuales que han pasado por CERCLES no volverán al sistema de ejecución penal](https://www.fsyc.org/insercion-social-y-empleo/nueve-de-cada-diez-condenados-por-delitos-sexuales-que-han-pasado-por-cercles-no-volveran-al-sistema-de-ejecucion-penal/)
- [COPE — Un informe de Prisiones aclara el mito de que un agresor sexual es irrecuperable: ¿Cuántos reinciden?](https://www.cope.es/programas/la-linterna/noticias/informe-prisiones-aclara-mito-que-agresor-sexual-irrecuperable-cuantos-reinciden-20221003_2323058)
- [eldiario.es — El 93% de los condenados por violencia de género que participaron en un programa de tratamiento terapéutico no reincidieron](https://www.eldiario.es/andalucia/violencia-de-genero-reinsercion-justicia-justicia-reincidencia-instituciones-penitenciarias_1_1588561.html)
- [Abogado Penal Barcelona — La medida de libertad vigilada, obligatoria para los delincuentes sexuales](https://www.abogadopenalbarcelona.com/blog/la-medida-de-libertad-vigilada-obligatoria-para-los-delincuentes-sexuales)
- [Morez Abogados — Tabla completa de penas por delitos sexuales en España 2025](https://www.morezabogados.com/delitos-sexuales-espana-2025-penas-reforma-jurisprudencia/)
- [Abogacía Española — La sustitución de la pena privativa de libertad por la expulsión (art. 89 CP)](https://www.abogacia.es/actualidad/noticias/la-sustitucion-de-la-pena-privativa-de-libertad-por-la-expulsion-analisis-del-articulo-89-del-codigo-penal/)
- [Newtral — En qué casos España ya prevé la expulsión de extranjeros que hayan cometido un delito](https://www.newtral.es/expulsion-extranjeros-delito/20250929/)
- [Newtral — España ha expulsado a más de 140.000 inmigrantes desde que hay registros](https://www.newtral.es/inmigrantes-irregular-espana/20231218/)
- [Andalucía Información — Prisión provisional para un detenido por agresión sexual que ya estaba en tercer grado por casos similares](https://www.andaluciainformacion.es/articulo/granada/prision-provisional-detenido-agresion-sexual-que-estaba-tercer-grado-casos-similares/202606051251333397793.html)
- [Carlos CR Abogado Penalista — La Prisión Provisional: Requisitos Art. 503 LECrim](https://carloscr.es/articulos/la-prision-provisional-requisitos-art-503-lecrim/)
- [Periodista Digital — Los extranjeros suponen el 13,4% de la población pero están implicados en el 37,3% de los delitos sexuales](https://www.periodistadigital.com/gente/sucesos/20250904/extranjeros-suponen-134-poblacion-implicados-373-delitos-sexuales-noticia-689405128304/) — *unverified primary table, framing-heavy outlet, treat with caution*
- [The Objective — Los extranjeros cometen en proporción 5,2 veces más delitos sexuales que los españoles](https://theobjective.com/espana/2025-10-20/extranjeros-cometen-5-veces-mas-delitos-sexuales/) — *unverified primary table, framing-heavy outlet, treat with caution*
- [The Objective — El 46% de los condenados por agresión sexual en España tiene nacionalidad extranjera](https://theobjective.com/espana/2022-10-02/agresion-sexual-espana-extranjeros/) — *unverified, treat with caution*
- [CEU-CEFAS — Demografía de la delincuencia en España, Informe 21](https://cefas.ceu.es/wp-content/uploads/Informe_delincuencia_21_Observatorio_Demografico_CEU_CEFAS.pdf) — *advocacy-affiliated think tank, treat with caution*
- [Psyshei Psicología — Tasa de reincidencia según el tipo de delito: revisión de un estudio longitudinal](https://psyshei.com/tasa-de-reincidencia-segun-el-tipo-de-delito-revision-de-un-estudio-longitudinal)

## Open follow-ups for this repo (not yet done)

1. Extract CGPJ "Condenados" reincidencia field by offense subtype (flagged pending in the
   now-removed `data/haiku_artifacts/` notes — see git history pre-2026-07).
2. Verify or refute the foreigner/Spaniard sexual-recidivism percentages (~7.9% vs ~24.8%) against a
   primary INE/Instituciones Penitenciarias/CGPJ table — currently unsourced beyond a search-engine
   summary.
3. Reconcile the two 2024 "condenados" totals found (5,230 vs 3,936) against the actual INE/CGPJ
   publication.
4. Pull INE table 28716 (sexual crimes by perpetrator nationality) into CSV — already flagged as a gap
   in `SOURCES_INDEX.md`.
