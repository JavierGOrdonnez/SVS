# PPSA — Political Party Sexual & Gender-Based Abuse (Spain)

Sibling project to [SVS](../README.md). Reuses SVS's methodology (sourced,
confidence-tagged, invariant-checked data pipeline — see
`../SPEC.md`, `../VERIFICATION_GUIDE.md`) applied to a different question.
Independent scope: not merged into the SVS violence-probability model, not
reusing any of its datasets, and not accountable to its §T roadmap.

**Core question:** Among people who ever held a position obtained through a
Spanish political party (elected under its ticket, appointed by it to a
public post, or directly employed by the party apparatus), how many have
been subject to a judicial proceeding for sexual abuse/assault or
gender-based ("machista") violence — at any point before, during, or after
holding that position? How does the count, and the count **as a share of
each party's total headcount**, compare across parties and across the
ideological spectrum?

## Why this framing

Two failure modes to avoid, both flagged by the person who requested this
project:

1. **Numerator without denominator is meaningless.** A party with 10,000
   elected/appointed people over 20 years will rack up more raw cases than
   one with 200, with no implication about culture or vetting. Every
   headline count in Table 1 must be paired with the party's total
   qualifying headcount in Table 2, and reported as a rate.
2. **Unverified accusation ≠ finding.** Naming real people in connection
   with sexual-violence allegations carries real defamation and harm risk.
   See **C2** in `SPEC.md`: only entries with an actual judicial case
   number qualify, tagged by case status (open / convicted / acquitted).
   Press-only allegations with no judicial proceeding are tracked
   separately (§ Watch-list) and never counted in the tables.

## Scope

| Axis | Definition used |
|---|---|
| Qualifying position | Elected office won under the party's ticket (concejal, diputado autonómico/nacional, senador, eurodiputado, alcalde) **or** a public post the party appointed the person to (alto cargo, personal eventual/asesor) **or** direct employment by the party's own organization |
| Qualifying conduct | Sexual assault/abuse (CP arts. 178–189) or gender-based ("violencia de género"/"machista") physical, psychological or sexual violence against a partner/ex-partner, per Spanish criminal code categories |
| Time window | Case counts against the party if the person held a qualifying position at *any* time — the abusive conduct itself may predate, overlap, or postdate that tenure. Attribution-timing rule is decided in `SPEC.md` C6. |
| Case status | `open` (denuncia/instrucción/procesamiento in progress), `convicted` (sentencia condenatoria — firme vs non-firme distinguished), `acquitted` (absuelto/sobreseído) |
| Evidentiary bar | Judicial proceeding only — see C2. No entry without a citable case reference. |

## Two tables

- **Table 1 — Raw counts per party**: number of distinct individuals with a
  qualifying judicial case, broken down by party × case status ×
  category (sexual vs. other gender-based violence).
- **Table 2 — Rate per party**: Table 1's counts divided by each party's
  total qualifying headcount over the same period (Table 2's own
  denominator table) — i.e. the proportion of each party's people who end
  up with a denuncia/condena. This is the number that actually supports or
  refutes an ideological-divide claim; Table 1 alone does not.

## Known hard problem: the denominator

Elected-office headcounts are reconstructable from official election
results archives (Ministerio del Interior, historical results by party per
election). Appointed posts and party-employed staff have **no centralized
public registry** — this is the gap the requester anticipated ("aunque eso
probablemente sea muy difícil de gestionar/investigar"). `SPEC.md` C4
documents this as an open research task rather than papering over it with
a guessed number.

## Status

Scaffold only — methodology, constraints, and source index committed;
no case data populated yet. See `SPEC.md` §T for the task breakdown before
any row is added to a dataset.

## Where to look

- `SPEC.md` — constraints, invariants, task roadmap.
- `data/sources/SOURCES_INDEX.md` — sources found so far, and the gaps.
- `data/raw/` — empty until §T1 (schema) and §T2 (first sourced cases) land.
