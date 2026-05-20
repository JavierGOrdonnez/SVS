# SVS — Sexual Violence in Spain

**Core question:** Given a woman born in 2000, living in Spain in 2025 — what is her probability of being raped, sexually assaulted, femicided, murdered, or suffering non-sexual violence in the next year, next 5 years, and over her remaining lifetime? Calculated assuming 2025 conditions persist.

**Follow-up:** Using historical data (2000–2025), how do those probabilities shift under changes in explanatory variables — e.g. far-right vote share, total immigration volume, or immigration broken down by origin, gender, and age cohort?

---

## Scope

| Violence type | Definition used |
|---|---|
| Rape / sexual assault | Crimes recorded under CP arts. 178–184 + victimisation surveys |
| Femicide | Intimate-partner and family homicides of women (official CGPJ/Ministerio registry) |
| Homicide (other) | All other female homicide victims |
| Non-sexual violence | Physical assaults recorded against women (domestic + non-domestic) |

## Data sources (planned)

- **Ministerio del Interior** — crime statistics (estadísticasdelcrimen)
- **CGPJ** — femicide observatory annual reports
- **Delegación del Gobierno contra la Violencia de Género** — macroencuesta de violencia contra la mujer
- **INE** — population, mortality, and demographic tables
- **Eurostat / CIS** — political and immigration indicators

## Methodology (planned)

1. Collect and clean annual time-series (2000–2025) for each violence type.
2. Compute incidence rates per 100 000 women, age-standardised to the 2000-born cohort.
3. Apply actuarial (competing-risks) life-table to convert annual rates → 5-year and lifetime cumulative probabilities.
4. Fit multivariate regression / Bayesian structural time-series to estimate partial effects of covariates (far-right vote share, immigration volume/composition, etc.).
5. Produce scenario projections: "what if covariate X changes by ±N%?"

## Caveats

- Official crime statistics capture *reported* crimes; dark-figure estimation requires survey cross-validation.
- Femicide definitions vary across sources and years; methodology notes document each reconciliation decision.
- Correlation ≠ causation. Covariate analysis is descriptive / associative, not causal.
- Lifetime probability estimates assume constant 2025 rates; actual future risk depends on social and policy changes.

## Repo layout (evolving)

```
data/        raw + cleaned data files
notebooks/   exploratory analysis
src/         data pipeline and modelling code
reports/     outputs and write-ups
```

## Status

Early stage — data collection and pipeline setup in progress.
