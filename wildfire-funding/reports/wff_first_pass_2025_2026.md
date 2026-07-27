# WFF — First-pass wildfire-funding comparison

Scaffold-stage output — see `../SPEC.md` C2/C3/C7 for why this is a first
pass, not a finished result: spending figures are `confidence=low` and
several carry unresolved scope/source conflicts (see `notes` column in
`wff_spending.csv`). Canarias is excluded (no consolidated regional
total found). `pct_of_total_budget` is blank whenever the spend year and
the region's total-budget year are more than 1 year apart (most of the
historical Andalucía rows below) — better a gap than a misleading ratio.

## Latest year per CCAA, normalized three ways

| CCAA | Year | Spend (€M) | Coverage | € / 100k hab | € / km² forest | % of own budget |
|---|---|---|---|---|---|---|
| Comunidad Valenciana | 2026 | 298.5 | total | 5,611,092 | 23,557 | 0.896% |
| País Vasco | 2025 | 100.2 | total | 4,497,945 | 20,375 | 0.612% |
| Comunidad de Madrid | 2026 | 52.7 | total | 751,862 | 12,025 | 0.172% |
| Principado de Asturias | 2026 | 78.0 | total | 7,725,840 | 10,124 | 1.115% |
| Galicia | 2026 | 190.0 | total | 7,021,867 | 9,310 | 1.334% |
| Cantabria | 2026 | 26.3 | total | 4,451,207 | 7,219 | 0.670% |
| Comunidad Foral de Navarra | 2025 | 42.7 | total | 6,294,843 | 7,184 | 0.633% |
| Andalucía | 2026 | 300.0 | total | 3,475,496 | 6,716 | 0.581% |
| La Rioja | 2026 | 20.0 | total | 6,169,336 | 6,432 | 0.944% |
| Región de Murcia | 2026 | 28.0 | total | 1,785,154 | 5,476 | 0.416% |
| Castilla y León | 2026 | 222.7 | total | 9,311,439 | 4,625 | 1.417% |
| Extremadura | 2026 | 116.8 | total | 11,074,439 | 4,066 | 1.319% |
| Castilla-La Mancha | 2026 | 126.0 | total | 5,987,361 | 3,502 | 0.977% |
| Islas Baleares | 2025 | 6.5 | partial | 527,697 | 2,925 | 0.087% |
| Aragón | 2026 | 54.0 | total | 3,995,291 | 2,065 | 0.590% |
| Cataluña | 2026 | 18.0 | partial | 224,657 | 896 | 0.037% |

## Time series (CCAAs with more than one sourced year)

Only Andalucía (Plan INFOCA, 2020-2026) and Castilla-La Mancha (Plan
INFOCAM, 2025-2026) have more than one sourced year so far — everything
else is still a single snapshot. See `SPEC.md` T8 for extending this.

| CCAA | Year | Spend (€M) | € / 100k hab | € / km² forest |
|---|---|---|---|---|
| Andalucía | 2020 | 171.9 | 1,991,459 | 3,848 |
| Andalucía | 2021 | 175.1 | 2,028,531 | 3,920 |
| Andalucía | 2023 | 223.0 | 2,583,452 | 4,992 |
| Andalucía | 2024 | 244.0 | 2,826,737 | 5,462 |
| Andalucía | 2026 | 300.0 | 3,475,496 | 6,716 |
| Castilla-La Mancha | 2025 | 116.0 | 5,512,174 | 3,224 |
| Castilla-La Mancha | 2026 | 126.0 | 5,987,361 | 3,502 |

## Reading notes

- Ranking absolute spend is not the same ranking as any of the three
  normalizations — that's the point of computing them (README.md's
  core motivation).
- `coverage=partial` rows (Cataluña, Islas Baleares) understate the true
  figure — their normalized values are floors, not full pictures.
- Andalucía's own series (171.9M → 175.1M → 223M → 244M → 300M,
  2020-2026) shows nominal spend nearly doubling in six years — but this
  is *budgeted/announced* spend, not audited *executed* spend; the two
  can differ substantially once a season's actual fire severity forces
  extraordinary in-year credits. No region's liquidación (executed)
  figure has been sourced yet — see `SPEC.md` T9.
- Every absolute-spend row above has at least one unresolved
  conflicting/alternate figure documented in `wff_spending.csv`'s
  `notes` column — treat this table as directional, not final, until
  T2/T3 trace each figure to its primary budget-law source.
