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

First real data pass landed: 16 of 17 CCAAs have at least one sourced
2025/2026 wildfire-spend figure, all three normalizations now compute
(population, forest area, and — for 15 of those 16 — % of the region's own
total budget), and a small time series has started for two regions
(Andalucía 2020-2026, Castilla-La Mancha 2025-2026).
`analysis/compute_normalized.py` writes `reports/wff_first_pass_2025_2026.md`.

**Read this before citing anything from it**: every spend figure is
`confidence=low` (one `medium`), most have an unresolved conflicting
alternate figure from a second source, and the prevention/extinction
category split was explicitly deprioritized in favor of getting all
regions covered — see `SPEC.md` T1–T3. This is a directional first look,
not a verified result.

**Budgeted is not executed, and executed is the number that actually
matters** (per your steer). This is no longer just a caveat — real
executed (liquidado) figures now exist for 5 program×year pairs (see
`reports/wff_first_pass_2025_2026.md`'s Execution rate table), each
traced to the region's own ejecución presupuestaria / Compte General /
open-data budget-execution extract, not a press aggregator:

| CCAA | Year | Program | Execution % |
|---|---|---|---|
| Castilla y León | 2025 | Prevención y extinción de incendios | 48.5% (mid-year, pre-fire-season) |
| Cataluña | 2021 | Bombers (broader than wildfire-only) | 106.6% |
| Extremadura | 2024 | Total investment programs | 40.8% |
| Extremadura | 2024 | Lucha contra incendios forestales (narrowest line) | 8.9% |
| País Vasco / Bizkaia | 2023 | Medidas contra incendios forestales | 0€ initial credit → 1.34M executed |

Galicia also now has 6 years of presupuestado detail (2019-2021,
2023-2025), all partial investment-line slices of PLADIGA. Aragón got real
search effort (Cámara de Cuentas audits, Cortes written answers) but no
presupuestado/liquidado pair — documented as a gap rather than filled with
a guess.

**Madrid — the project's original cue — got the deepest dig, in three rounds.**
Round 2 established *why* no clean wildfire-specific budget line exists:
inspected Madrid's full official budget-by-program spreadsheet (~100
programs) directly and confirmed there is no "incendios forestales"
program at all — it's split across a forestry/biodiversity program (51.4M,
2026) and the general Bomberos corps (280M, too broad to use); the
announced 52.7M INFOMA figure is a cross-program estimate, not a
traceable line. Round 3, prompted by the user asking specifically for
journalistic leads given the 2026 fires: found a **court-adjudicated**
finding, not a mere allegation — the Tribunal Superior de Justicia de
Madrid ruled on 2026-01-13 that the regional government diverted ~€40M
(2019-2023) of legally earmarked firefighting-investment funds (the
national insurance-premium surcharge that by law must fund fire-service
capital investment) into current expenses like vehicle leasing instead —
a ruling now resurfacing in press coverage of the current fire season,
explicitly linked by the firefighters' union to present capacity gaps
(40+ vehicles out of service). Corroborated independently across
publico.es, infobae.com, and an insurance-trade outlet with no political
angle. Not added as a spending-data row (it's a 5-year cumulative figure
for a funding stream, not a program-year line item) but documented in
full in `SOURCES_INDEX.md` as the strongest lead found for Madrid.

The Tier-1 official all-CCAA parser (`parsers/parse_hacienda_totals.py`,
Hacienda's two SGCIEF portals) is confirmed working and now running
successfully in the background (resumability fix held after an earlier
crash) — see `SPEC.md` T8-T10 for current coverage.

## Where to look

- `SPEC.md` — constraints, invariants, task roadmap.
- `data/sources/SOURCES_INDEX.md` — official sources and NGO/press reports, incl. per-row citations for every populated figure.
- `data/raw/wff_spending.csv`, `wff_denominators.csv` — the actual data.
- `analysis/compute_normalized.py` → `reports/wff_first_pass_2025_2026.md` — the first cross-CCAA comparison.
