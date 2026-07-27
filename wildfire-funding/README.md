# WFF — Wildfire Prevention & Extinction Funding by Spanish Region

Sibling project to [SVS](../README.md). Reuses SVS's methodology (sourced,
confidence-tagged, invariant-checked data pipeline — see `../SPEC.md`,
`../VERIFICATION_GUIDE.md`) applied to a different question. Independent
scope: not merged into the SVS violence-probability model, not reusing any
of its datasets.

**Core question:** How much money does each Spanish autonomous community
(CCAA) spend per year on wildfire prevention and extinction — split by
category where the data allows — and how does that compare across regions
once normalized for population, forest area, and each region's own total
budget? Raw totals mislead here: CCAAs vary enormously in size, population,
forest cover, and fiscal capacity, so a comparison only means something
once normalized.

## Context (why now)

2025 was the worst wildfire year of the century in Spain by burned area;
2026 is already tracking worse in some metrics as of this writing. The
recurring pattern — severe fire season → public attention → little
follow-through on prevention funding once the season ends — is exactly the
kind of claim this project is built to check against real budget numbers
rather than impression.

## What we're computing

- **A. Raw annual spend per CCAA**, split into `prevención` vs
  `extinción` wherever the region discloses that split, and a third
  explicit `no desglosado` (undisclosed/mixed) bucket where it doesn't —
  see the transparency caveat below, this split is itself a finding, not
  just an input.
- **B. Three normalizations, computed separately (not blended into one
  index)**:
  1. € per 100,000 inhabitants (population denominator, INE).
  2. € per km² of forest area (Cuarto Inventario Forestal Nacional /
     MITECO forest-surface data).
  3. Spend as % of the CCAA's own total approved budget (Ministerio de
     Hacienda's official CCAA budget portal).
- **C. Historical trend** (as far back as sourceable, national aggregate
  already found back to 2000, per-CCAA coverage TBD) — to test the "no
  measures taken, funding drops right after the fires" hypothesis directly
  against year-over-year prevention-budget changes.

## Known transparency problem (flagged up front, not discovered later)

Greenpeace's 2023 public-information request found that only **Galicia,
Extremadura, Castilla-La Mancha, and Baleares** publish budgets that
clearly separate prevention from extinction/management spending. Most
CCAAs report a single lumped "incendios forestales" or "medio natural"
figure. This means Table A's `no desglosado` bucket will likely be the
majority for most regions — that opacity is itself part of what this
project reports, not a gap to quietly fill by guessing a split.

## Status

Scaffold only — methodology, constraints, and source index committed; no
figures populated yet. See `SPEC.md` §T for the task breakdown.

## Where to look

- `SPEC.md` — constraints, invariants, task roadmap.
- `data/sources/SOURCES_INDEX.md` — official sources and NGO/press reports found so far.
- `data/raw/` — empty until §T1 (schema) and §T2 (first sourced year) land.
