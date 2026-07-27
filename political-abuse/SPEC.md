# SPEC.md — PPSA (Political Party Sexual & Gender-Based Abuse, Spain)

Entry point for anyone (human or agent) working in `political-abuse/`.
Structured after SVS's `../SPEC.md` (§G/§C/§R/§I/§V/§T sections) for
consistency, but this project's data, invariants, and roadmap are entirely
separate from SVS's violence-probability model.

---

## §G — Goal

For each Spanish political party, identify every distinct individual who
(a) ever held a qualifying position obtained through that party, and (b)
has a judicial proceeding (open, convicted, or acquitted) for sexual abuse
or gender-based violence. Produce:

- **Table 1**: raw counts per party × case status × category.
- **Table 2**: those counts as a percentage of each party's total
  qualifying headcount over the same period — the actual comparable rate.

Then check whether the rate clusters by ideology (left/right), by
individual party, or is roughly uniform across the spectrum.

---

## §C — Constraints

C1: ∀ entry → cite the specific judicial source: court name, case/docket
number (if public), and the outlet or official bulletin reporting it. A
name with no citable judicial reference does not enter the dataset.

C2: **Evidentiary bar = judicial proceeding only.** Qualifying statuses:
`open` (denuncia admitted / instrucción / procesamiento under way),
`convicted` (sentencia condenatoria — record whether firme or under
appeal), `acquitted` (absuelto or sobreseído). Media-only allegations with
no judicial case are excluded from Table 1/Table 2 entirely; if tracked at
all, they go in a clearly separate, clearly labeled watch-list file that is
never summed into the party tables. This bar exists specifically to avoid
defamation and to keep every published number defensible.

C3: `open` status is a snapshot, not a verdict — presumption of innocence
applies. Every dataset export and any downstream chart must display status
distribution (open vs. convicted vs. acquitted) rather than collapsing to
a single "accused" count.

C4: **Denominator problem (headcount per party).** Elected offices
(concejal, diputado autonómico, diputado nacional, senador, eurodiputado,
alcalde) are reconstructable from Ministerio del Interior historical
election-results archives. Appointed posts (altos cargos, personal
eventual/asesores) and direct party employees have no centralized public
registry as of this writing — this is an open research task (see §T),
not something to estimate by guesswork. Until resolved, Table 2 must
either (a) restrict the denominator to elected officials only and say so
explicitly in every table caption, or (b) carry an explicit "denominator
incomplete" flag next to any figure that tries to include appointees/staff.

C5: Person disambiguation: full name + role + municipality/region + years
in office, minimum, to avoid conflating homonyms. Where a case reference
(docket number) is available, store it — it is the strongest
disambiguator.

C6: **Party-attribution-at-time-of-fact rule.** A person who changed party
(transfuguismo) or whose case predates/postdates their tenure is attributed
to **every** party under which they held a qualifying position during the
period covered, not only the party they belonged to when the alleged
conduct occurred. Each dataset row records the specific party+position+date
range it is attributed to, so a person can appear in more than one party's
row set without double-counting in a combined total.

C7: Table 2's denominator must be computed over the **same time window**
as its numerator (e.g., "individuals holding a qualifying position at any
point 2000–2025" on both sides), never a raw current-day headcount divided
into a historical case count.

C8: Party mergers/renames/splits (e.g., Podemos → Sumar coalition
dynamics, Ciudadanos dissolution) must be documented explicitly per row;
⊥ silently mapped to whichever successor party is currently prominent.

C9: All confidence-tagging conventions from `../SPEC.md` C1/C12 (source
citation, `confidence` field, `unverified` rows excluded from any public
figure) apply here unchanged.

---

## §R — Research (open questions, not yet resolved)

R1: Is there an existing registry, academic dataset, or journalistic
tracker that already compiles judicial cases against Spanish
politicians for sexual/gender violence, across all major parties? Initial
search turned up individual case reporting (see `data/sources/SOURCES_INDEX.md`)
but no single comprehensive, judicially-sourced tracker — confirm this
absence more rigorously before committing to fully manual compilation.

R2: Best source for the appointee/staff denominator (C4). Candidates to
investigate: Portal de Transparencia (national + autonomous), BOE "personal
eventual" appointment notices, party-level financial disclosures to the
Tribunal de Cuentas (which list some staff), FOI requests to each party
headquarters. Likely no clean answer — document whatever partial coverage
is achievable and its limitations.

R3: CGPJ judicial statistics (`poderjudicial.es`) publish
gender-violence/sexual-crime conviction stats by age/sex/nationality of the
convicted person, but **not** by profession or political affiliation —
confirmed by an initial search pass. This means there is no shortcut via
aggregate judicial statistics; every entry has to be sourced as an
individual, named case.

---

## §I — Interfaces

```
file: data/raw/ppsa_cases.csv            → one row per (person, party, position, case) — schema TBD in T1
file: data/raw/ppsa_headcounts.csv       → one row per (party, position-type, period) → total qualifying headcount — schema TBD in T1
file: data/sources/SOURCES_INDEX.md      → living index of sources consulted, incl. R1/R2/R3 findings
```

---

## §V — Invariants

V1: ∀ row in `ppsa_cases.csv` → `person_name`, `party`, `position`,
`date_range`, `case_status` ∈ {open, convicted, acquitted}, `category` ∈
{sexual, gender-based-other}, `source_name`, `source_ref` (docket number or
URL), `confidence` — all non-empty.

V2: ∀ row in `ppsa_headcounts.csv` → `party`, `position_type`, `period`,
`headcount`, `source_name`, `coverage_note` (does this headcount include
appointees/staff or elected-only? per C4) — all non-empty.

V3: sum of Table 1 case counts for a party ⊥ ever divided by a headcount
whose `coverage_note` scope doesn't match the case set's own position
scope (elected-only cases ÷ elected-only headcount; never elected-only
cases ÷ a headcount that also includes appointees, or vice versa).

V4: No public-facing table, chart, or summary may display a rate (Table 2)
without also showing/link to the absolute counts (Table 1) and the
denominator it used — rates alone invite misreading a small-N party as
categorically worse.

---

## §T — Tasks

| id | status | track | what/where |
|---|---|---|---|
| T1 | . | infra | Design `ppsa_cases.csv` / `ppsa_headcounts.csv` schemas satisfying V1/V2; decide category taxonomy (sexual vs. other gender-based violence) precisely against CP articles. |
| T2 | . | data | Compile first sourced batch of judicial cases (any party) from `data/sources/SOURCES_INDEX.md` leads — PSOE, PP, Vox, (Unidas) Podemos/Sumar cases already surfaced there are the starting point. |
| T3 | . | data | Resolve R1: confirm/refute existence of a prior comprehensive tracker before continuing manual compilation. |
| T4 | . | data | Build elected-official headcount per party per period from Ministerio del Interior historical election-results archives (C4 elected-only branch). |
| T5 | . | research | Investigate R2 (appointee/staff denominator) — Portal de Transparencia, Tribunal de Cuentas party filings, direct party FOI requests; document whatever partial answer is found, including "no data" as a documented outcome. |
| T6 | . | analysis | Once T2 (numerator) and T4 (denominator, elected-only) both have ≥1 full election cycle of coverage, build Table 1 and Table 2 (elected-only view) and check for ideological clustering. |
| T7 | . | analysis | Extend Table 2 to incorporate T5's appointee/staff denominator once available, with the V3 scope-matching invariant enforced. |
