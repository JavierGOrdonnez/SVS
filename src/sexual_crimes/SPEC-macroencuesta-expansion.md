# SPEC-macroencuesta-expansion.md — Macroencuesta de Violencia contra la Mujer, beyond T98/T99

Part of the SVS spec. Top-level goal/shared constraints/invariants/roadmap/bug
log live in [`SPEC.md`](../../SPEC.md); this file owns §T tasks T100-T106.

Scope note: this file is a **plan, not a build log** — every task below is
status `.` (not started). It exists because T98/T99 ([`SPEC-sexual-crimes.md`](SPEC-sexual-crimes.md))
only mined one chapter (16, "violencia sexual fuera del ámbito de la pareja")
out of a ~20-chapter, 340-401-page survey per wave. This document is the
output of a systematic pass over both wave PDFs' full tables of contents
(`data/sources/Macroencuesta_{2019,2024}.pdf`) to catalogue what else is in
there, with exact table numbers/pages verified against the real PDF text —
not guessed from a TOC listing — so a future implementer doesn't have to
redo the spelunking. Requested directly: "create a new spec for all these
investigations... I will read the report later myself and see how it fits
into this all."

All tasks build on T99's infrastructure: `src/parsers/macroencuesta_parser.py`
already has the two page-location primitives needed (`_locate_page` — content-
keyword scan, not hardcoded page numbers; `_page_window_text` — join N pages
so a table spanning a page break isn't truncated) and the two proven table-
shape parsers (`_find_si_ic_block` for "Sí ... / IC 95% (...)" prevalence-style
blocks; the label-then-numeric-tokens pattern used for relationship rows).
Every task below reuses one or both rather than inventing a new extraction
strategy.

---

## §I — Interfaces (planned, none exist yet)

```
file: data/raw/macroencuesta_partner_2019-2024.json    → PLANNED (T100). Prevalence of physical/sexual/combined violence BY partner (Cap. 1-3), lifetime/4yr/12mo, current vs. past partner split — the partner-violence mirror of what macroencuesta_2019-2024.json already holds for outside-partner violence.
file: (extends macroencuesta_partner_2019-2024.json)   → PLANNED (T101). Partner-perpetrator nationality ("País de nacimiento de la pareja actual/pasada") from Tabla 1.18 (physical), Tabla 3.16 (combined), and Chapter 2's equivalent (sexual-only, page not yet pinned — see T101 caveat) — both waves.
file: (extends macroencuesta_2019-2024.json)            → PLANNED (T102). Reporting behavior: denuncia rate, who filed it, reasons for NOT reporting, satisfaction with police response — Cap. 16.8 (outside-partner) + Cap. 9 (partner), both waves.
file: (extends macroencuesta_2019-2024.json)            → PLANNED (T103). Sociodemographic breakdown of outside-partner prevalence: age, victim's own birth country, education, employment/income, disability, municipality size — Cap. 16.2, both waves.
file: (extends macroencuesta_2019-2024.json)            → PLANNED (T104). Assault context: location (Cap. 16.5) + prior online interaction (Cap. 16.6), outside-partner, both waves.
file: (extends macroencuesta_2019-2024.json)            → PLANNED (T105). Frequency + single-vs-multiple-perpetrators, outside-partner (Cap. 16.3, Tabla ~16.18), both waves.
file: (extends macroencuesta_2019-2024.json)            → PLANNED (T106). Consequences: injuries, psychological impact, substance use, disability, work absence — Cap. 16.9, both waves.
```

## §V — Invariants (apply to any task in this file)

V47: **Wave comparability break still applies.** The 2024 methodology change vs. 2019 (`macroencuesta.md`'s existing caveat) is not specific to the relationship/prevalence tables T98/T99 already extracted — it applies to every table in this document equally. Any task below that reports a 2019→2024 delta ! flag it the same way `macroencuesta.md` already does for the headline prevalence figures: measurement-change and real-change are both live explanations, not distinguishable from the survey alone.

V48: **The chapter-15-vs-16 lookalike-table bug (T99) is a *pattern*, not a one-off.** Both waves structure "violencia física en/fuera de la pareja" and "violencia sexual en/fuera de la pareja" as parallel chapters with near-identical table titles and row labels (confirmed for chapters 1 vs. 2 vs. 3 vs. 15 vs. 16 specifically). Any task in this file that locates a table by keyword ! verify the located page actually falls within the intended chapter's page range (anchor past that chapter's own heading first, exactly as `Macroencuesta2019Parser.parse()` now does for chapter 16) before trusting a match — do not assume a single distinctive-sounding keyword pair is safe just because it looks unique in isolation (T99's original bug looked exactly this safe until it wasn't).

V49: **Suppression/small-sample markers are meaningful, not noise.** Confirmed across multiple tables (Tabla 1.18, 3.16, 16.21): a bare `.` means the cell is suppressed (sample <6, no figure given — must stay `None`, never coerced to 0), and a leading `¨` (e.g. `¨4,9`) flags a small-but-real sample (6-19 observations, "use with caution" per the report's own footnote) — the number itself is real data and must be kept, not dropped alongside genuine `.` suppressions. `macroencuesta_parser.py`'s `_split_tokens_2024` already implements this distinction correctly for Tabla 16.21; any new 2024-wave table parser ! reuse the same convention rather than re-deriving it.

## §T — Tasks (all status `.`, not started)

| id | status | track | task | cites |
|---|---|---|---|---|
| T100 | . | B,D | **Partner-violence prevalence, base extraction.** Chapters 1 (physical), 2 (sexual), 3 (combined) each have their own "Tabla X.1 Prevalencia... a lo largo de la vida, en los últimos 4 años, en los últimos 12 meses" using the exact same `Sí <pct> <N> ... / IC 95% (...)` shape T99 already parses (`_find_si_ic_block`) — confirmed for chapter 2's Tabla 2.18/2.19 (prevalence of sexual violence AND specifically violación, by partner, both "pareja actual" and "parejas pasadas" columns, which chapter 16 doesn't have since a stranger/acquaintance obviously isn't "current" vs "past"). This is the prerequisite for T101 (nationality) and the partner side of T102 (reporting) — build it first. Design note: partner tables add a `pareja actual` vs. `parejas pasadas` vs. `cualquier pareja` column split that outside-partner tables don't have; the schema needs a `partner_status` field (`current`/`past`/`any`) alongside `timeframe`, not just a wider `TIMEFRAMES` list. | V47,V48 |
| T101 | . | B,D | **Partner-perpetrator nationality** — the highest-value item here, given the project's existing nationality-trend focus (crime/SPEC-crime.md's peligrosidad work, migration correlation analysis) and the explicit ask that prompted this file ("we see an increase for all nationalities, including Spanish perpetrators... put into perspective the police records"). Verified live in the 2024 PDF: Tabla 1.18 (physical, p.32 in this session's pdfplumber index) and Tabla 3.16 (combined, p.63) both have a "País de nacimiento de la pareja actual" row — España vs. Otro país — cross-tabbed against whether that partner exercised violence or not: e.g. Tabla 3.16, 22.7% "Otro país" among partners who exercised physical-and/or-sexual violence vs. 15.0% among those who didn't (p<0.01). This is a **population-based comparison of partner nationality by violence-perpetration status**, immune to the reporting-bias question entirely (it doesn't matter whether anything was ever reported to police) — the closest thing to survey-side "perpetrator nationality" data this repo has found. Chapter 2 (sexual-only) almost certainly has its own equivalent table nearby its own end (section "2.1.7 ... características sociodemográficas de la pareja agresora" is in the TOC) but its exact page wasn't pinned this session — search for "PAIS DE NACIMIENTO" + "PAREJA ACTUAL" scoped to chapter 2's page range (same `_locate_page` pattern, applying V48's anchor-past-chapter-start discipline). Depends on T100 for the surrounding prevalence context (this table is naturally attached to the same chapters). | V47,V48,V49 |
| T102 | . | B,D | **Reporting behavior — the "more reporting vs. more incidents" question, directly.** Both chapters have a whole reporting sub-tree: Cap. 16.8 (outside-partner) — 16.8.1.1 denuncia rate, 16.8.1.2 who filed it, 16.8.1.3 timing, 16.8.1.4 satisfaction with police, 16.8.1.5 **reasons for not reporting**; Cap. 9 (partner) has the parallel structure (9.1.1-9.1.5, same shape, "motivos para no denunciar la violencia de la pareja" at 9.1.4). The reasons-for-not-reporting breakdown is the most directly useful piece for the stated goal: if the "more reporting, not more incidents" story is real, the *distribution* of reasons should shift between waves (e.g. less "no le di importancia"/"pensé que no me creerían", more "se solucionó de otra manera") even where raw prevalence looks flat — a signal raw prevalence alone can't give you. Table shape not yet inspected this session (only the TOC was read) — first step is a page-location + `extract_text()` dump of 16.8.1.5 and 9.1.4 in both waves to determine format before writing an extractor. | V47,V48 |
| T103 | . | B,D | Sociodemographic breakdown of outside-partner sexual-violence prevalence (Cap. 16.2: 16.2.1 age, 16.2.2 victim's own birth country/education/municipality size, 16.2.3 employment/income, 16.2.4 disability, 16.2.5 interview mode). Lets you check whether the 2017-2024 MIR trend (and any 2019→2024 Macroencuesta shift) concentrates in a demographic subgroup rather than being uniform — e.g. the age breakdown already glimpsed in prose (2019: 18-24 highest at 11.5%, 65+ lowest at 2.8%) suggests age-structure effects worth quantifying properly rather than reading off narrative text. Note: victim's own birth country (16.2.2) is NOT perpetrator nationality — don't conflate with T101; this is about who reports being victimized, a different question from who the aggressor was. | V47 |
| T104 | . | C,D | Assault context: location (Cap. 16.5 — own home, aggressor's home, other's home, street/open space, festive/nightlife settings, etc., already partially seen for rape specifically: 68.5% "en una casa" per 2024 prose) and prior online interaction (Cap. 16.6 — relevant given rising concern about app/online-facilitated assault specifically; not yet inspected in detail this session). Context/description rather than a trend-comparison input — lower priority than T100-T103. | V47 |
| T105 | . | B,D | Frequency of violence + single-vs-multiple perpetrators, outside-partner (Cap. 16.3). Partially seen already: 2024's Tabla 16.18 gives % of victims where "más de una persona" participated, by severity tier (11.3% rape, 7.6% attempted, 10.0% other) — same `Sí`-block shape T99 handles, just a different % basis (participation flag, not prevalence). Feeds a "how often is this a solo-offender vs. group event, and does that vary with severity" question, adjacent to the repo's existing `MIR_GroupSexualViolence_2023.pdf`/ONVIOS group-violence material (`fuentes_secundarias_analisis_espana.md`) — could eventually cross-reference rather than duplicate. | V47 |
| T106 | . | C,D | Consequences (Cap. 16.9: injuries by type, medical care sought, psychological consequences, substance use to cope, disability, work absence, self-perceived health/suicidal ideation, insecurity perception). Public-health framing rather than a crime-trend input — lowest priority of the tasks here, listed for completeness since it's in the same chapter as everything else and cheap to add once the chapter-16 page-location scaffolding exists for T103-T105. | V47 |

## Suggested build order

T100 → T101 (nationality needs the partner-prevalence scaffolding first) →
T102 (reporting, the other headline-relevant piece, independent of T100/T101
but similarly high-value) → T103/T104/T105/T106 (outside-partner chapter-16
extensions, lower individual priority, cheap to batch together once one of
them is built since they share the same chapter's page-location logic).

## Related bugs

None yet — no code exists for these tasks. T99's chapter-15-vs-16 collision
(B-numbered in `SPEC.md` §B once assigned, or see T99's own entry in
[`SPEC-sexual-crimes.md`](SPEC-sexual-crimes.md) for the full writeup) is the
precedent V48 above generalizes from.
