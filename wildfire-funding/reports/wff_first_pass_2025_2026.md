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
| Castilla y León | 2025 | 104.3 | 4,360,948 | 2,166 |
| Castilla y León | 2025 | 50.6 | 2,115,666 | 1,051 |
| Castilla y León | 2026 | 222.7 | 9,311,439 | 4,625 |
| Castilla-La Mancha | 2025 | 116.0 | 5,512,174 | 3,224 |
| Castilla-La Mancha | 2026 | 126.0 | 5,987,361 | 3,502 |
| Cataluña | 2020 | 212.9 | 2,656,822 | 10,599 |
| Cataluña | 2021 | 237.5 | 2,963,926 | 11,825 |
| Cataluña | 2021 | 253.1 | 3,158,913 | 12,602 |
| Cataluña | 2026 | 18.0 | 224,657 | 896 |
| Extremadura | 2024 | 10.1 | 959,532 | 352 |
| Extremadura | 2024 | 72.4 | 6,861,790 | 2,519 |
| Extremadura | 2024 | 29.5 | 2,797,054 | 1,027 |
| Extremadura | 2024 | 1.1 | 106,193 | 39 |
| Extremadura | 2024 | 0.1 | 9,482 | 3 |
| Extremadura | 2026 | 116.8 | 11,074,439 | 4,066 |
| Galicia | 2019 | 6.3 | 233,939 | 310 |
| Galicia | 2019 | 3.3 | 121,294 | 161 |
| Galicia | 2019 | 2.5 | 93,779 | 124 |
| Galicia | 2020 | 10.8 | 398,449 | 528 |
| Galicia | 2020 | 7.2 | 267,074 | 354 |
| Galicia | 2020 | 4.6 | 169,776 | 225 |
| Galicia | 2020 | 3.1 | 115,047 | 153 |
| Galicia | 2021 | 11.4 | 421,591 | 559 |
| Galicia | 2021 | 4.7 | 172,717 | 229 |
| Galicia | 2021 | 4.4 | 161,737 | 214 |
| Galicia | 2021 | 1.9 | 70,044 | 93 |
| Galicia | 2023 | 14.9 | 550,750 | 730 |
| Galicia | 2023 | 11.1 | 411,186 | 545 |
| Galicia | 2023 | 7.8 | 286,479 | 380 |
| Galicia | 2023 | 2.8 | 105,186 | 139 |
| Galicia | 2024 | 7.3 | 270,397 | 359 |
| Galicia | 2024 | 6.0 | 221,743 | 294 |
| Galicia | 2024 | 5.6 | 207,404 | 275 |
| Galicia | 2024 | 5.6 | 206,812 | 274 |
| Galicia | 2024 | 3.7 | 136,045 | 180 |
| Galicia | 2025 | 15.8 | 585,291 | 776 |
| Galicia | 2025 | 6.0 | 220,339 | 292 |
| Galicia | 2025 | 3.9 | 144,133 | 191 |
| Galicia | 2026 | 190.0 | 7,021,867 | 9,310 |
| País Vasco | 2023 | 0.0 | 0 | 0 |
| País Vasco | 2023 | 1.3 | 60,195 | 273 |
| País Vasco | 2025 | 100.2 | 4,497,945 | 20,375 |

## Execution rate (liquidado / presupuestado), per CCAA x year x program

The actual novel output this round: every (ccaa, year, program_name) pair
where *both* a presupuestado and a liquidado row exist (SPEC.md T9). This is
still a small, opportunistic sample — most rows in this dataset only have
one side of the pair — but it's real, sourced, and already shows the
under-execution pattern the project set out to check for.

| CCAA | Year | Program | Presupuestado (€) | Liquidado (€) | Execution % |
|---|---|---|---|---|---|
| Castilla y León | 2025 | Programas de Prevención y Extinción de incendios | 104,300,000 | 50,600,000 | 48.5% |
| Cataluña | 2021 | Prevenció, extinció d'incendis i salvaments | 237,476,600 | 253,099,400 | 106.6% |
| Extremadura | 2024 | Lucha contra incendios forestales (proyecto) | 1,120,000 | 100,000 | 8.9% |
| Extremadura | 2024 | Total Investment Programs (Protección y defensa contra incendios + Conservación, protección e mejora de montes) | 72,370,000 | 29,500,000 | 40.8% |
| País Vasco | 2023 | Medidas contra incendios forestales | 0 | 1,340,946 | N/A (0 initial credit) |

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
  extraordinary in-year credits (see the Execution rate table above for
  concrete examples: Extremadura's narrowest project line hit 8.9%
  execution in 2024, and País Vasco/Bizkaia's wildfire project had a
  0-euro initial credit that still ended up executing 1.34M via in-year
  credit modification).
- Every absolute-spend row above has at least one unresolved
  conflicting/alternate figure documented in `wff_spending.csv`'s
  `notes` column — treat this table as directional, not final, until
  T2/T3 trace each figure to its primary budget-law source.
