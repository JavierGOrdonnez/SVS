# WFF — First-pass normalized comparison (2025/2026 spend, 2024 population, 2019 forest area)

Scaffold-stage output — see `../SPEC.md` C2/C3/C7 for why this is a first
pass, not a finished result: spending figures are `confidence=low` and
several carry unresolved scope/source conflicts (see `notes` column in
`wff_spending.csv`). Canarias is excluded (no consolidated regional
total found). Total-CCAA-budget normalization (% of own budget) is not
yet computed — `total_budget_eur` is still pending (T6).

| CCAA | Year | Spend (€M) | Coverage | € / 100k hab | € / km² forest |
|---|---|---|---|---|---|
| Comunidad Valenciana | 2026 | 298.5 | total | 5,611,092 | 23,557 |
| País Vasco | 2025 | 100.2 | total | 4,497,945 | 20,375 |
| Comunidad de Madrid | 2026 | 52.7 | total | 751,862 | 12,025 |
| Principado de Asturias | 2026 | 78.0 | total | 7,725,840 | 10,124 |
| Galicia | 2026 | 190.0 | total | 7,021,867 | 9,310 |
| Cantabria | 2026 | 26.3 | total | 4,451,207 | 7,219 |
| Comunidad Foral de Navarra | 2025 | 42.7 | total | 6,294,843 | 7,184 |
| Andalucía | 2026 | 300.0 | total | 3,475,496 | 6,716 |
| La Rioja | 2026 | 20.0 | total | 6,169,336 | 6,432 |
| Región de Murcia | 2026 | 28.0 | total | 1,785,154 | 5,476 |
| Castilla y León | 2026 | 222.7 | total | 9,311,439 | 4,625 |
| Extremadura | 2026 | 116.8 | total | 11,074,439 | 4,066 |
| Castilla-La Mancha | 2026 | 126.0 | total | 5,987,361 | 3,502 |
| Islas Baleares | 2025 | 6.5 | partial | 527,697 | 2,925 |
| Aragón | 2026 | 54.0 | total | 3,995,291 | 2,065 |
| Cataluña | 2026 | 18.0 | partial | 224,657 | 896 |

## Reading notes

- Ranking absolute spend (Andalucía, Comunidad Valenciana, Galicia at the
  top) is not the same ranking as either normalization — that's the
  point of computing them (README.md's core motivation).
- `coverage=partial` rows (Cataluña, Islas Baleares) understate the true
  figure — their normalized values are floors, not full pictures.
- Every absolute-spend row above has at least one unresolved
  conflicting/alternate figure documented in `wff_spending.csv`'s
  `notes` column — treat this table as directional, not final, until
  T2/T3 trace each figure to its primary budget-law source.
