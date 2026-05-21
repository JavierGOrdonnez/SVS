# Source: INE — Population denominators for mortality rates

INE table 56934 "Estimaciones de la Población Actual de España" provides national-level population by single-year age × sex × quarterly reference date (Jan 1, Apr 1, Jul 1, Oct 1) from 1971 onwards.

We use **July 1 mid-year population** as the denominator for annual mortality rates — standard demographic practice (deaths occur throughout the year; mid-year approximates person-years of exposure).

---

## Source URLs

| Resource | URL |
|---|---|
| Table 56934 (browser UI) | https://www.ine.es/jaxiT3/Tabla.htm?t=56934 |
| CSV download | https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/56934.csv?nocab=1 |
| Operation page | https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176951 |

## Coverage

| Dimension | Values |
|---|---|
| Years | 1971–2025 (we aggregate 1971–2025 in long form; bins keep all years) |
| Reference dates | Jan 1, Apr 1, Jul 1, Oct 1 (some quarters suppressed pre-2002 with `..`) |
| Sex | `all`, `male`, `female` |
| Age | 109 single-year ages (0 to 99, 100, "100 y más", plus "Todas las edades") |
| Unit | Personas |

## Pipeline

```
curl -s "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/56934.csv?nocab=1" -o /tmp/ine_pop.csv
python3 src/parse_ine_population.py /tmp/ine_pop.csv
python3 src/compute_mortality_rates.py \
    data/processed/mortality_spain_ine_ecm.csv \
    data/processed/population_spain_midyear_5yr.csv
```

## Output files

| File | Rows | Description |
|---|---|---|
| `data/processed/population_spain_estimates.csv` | 35,805 | Long form: year × ref_date × sex × age_single × population |
| `data/processed/population_spain_midyear_5yr.csv` | 3,312 | July 1, aggregated to 5-yr age groups matching mortality data |
| `data/processed/mortality_rates.csv` | 198,000 | Full join: deaths × pop → rate/100k, every cause |
| `data/processed/mortality_rates_key.csv` | 11,550 | Subset: all-cause, homicide, suicide, traffic, drug, undetermined |
| `data/processed/mortality_rates_all_cause_by_age.csv` | 1,650 | Concise: year × sex × age all-cause only |

## Schema — `population_spain_midyear_5yr.csv`

| Column | Type | Example | Notes |
|---|---|---|---|
| `year` | int | 2024 | Reference year |
| `sex` | enum | `female` | `all` ∣ `male` ∣ `female` |
| `age_group` | enum | `15-19` | 22 groups matching mortality table 7947 |
| `population_july1` | int | 1287752 | Estimated population at July 1 |

## Schema — `mortality_rates.csv`

| Column | Type | Example | Notes |
|---|---|---|---|
| `year` | int | 2023 | |
| `sex` | enum | `female` | |
| `age_group` | enum | `30-34` | |
| `cause_chapter` | str | `IX` | Empty for sub-causes, `I-XXII` for grand total |
| `cause` | str | `Agresiones (homicidio)` | INE reduced-list cause name |
| `deaths` | int | 12 | Numerator |
| `population` | int | 1397777 | Mid-year denominator |
| `rate_per_100k` | float | 0.8585 | deaths / population × 100,000 |

## Age-group construction

To match mortality table 7947's bins, single-year ages are aggregated:

| Bin | Source ages |
|---|---|
| `<1` | "0 años" |
| `1-4` | "1 año" + "2 años" + "3 años" + "4 años" |
| `5-9` | "5 años" .. "9 años" |
| `10-14`, `15-19`, …, `90-94` | five-year sums |
| `95+` | "95 años" + "96 años" + "97 años" + "98 años" + "99 años" + "100 y más años" |

⚠ The table contains both "100 años" (single-year count) and "100 y más años" (open-ended ≥100 total). These overlap — only "100 y más años" is included in the 95+ bin. The 5,573 difference observed in 2024 female before this fix confirmed the double-count.

## Cross-checks performed

| Year | Sex | Bin sum | INE published all-ages | Delta |
|---|---|---|---|---|
| 2024 | female | 24,881,624 | 24,881,624 | 0 (exact) |
| 2024 | male | 23,940,312 | 23,940,312 | 0 (exact) |
| 2010 | female | 23,553,899 | 23,553,902 | 3 (single-year rounding) |

## Caveats

- **Mid-year vs Jan 1.** July 1 is closer to the centre of the year of exposure; Jan 1 (Padrón) underestimates exposure by ~half a year of cohort flow. Our rates use July 1.
- **Estimaciones vs Padrón Continuo.** Table 56934 is the demographic "Estimaciones de la Población Actual" — a model that adjusts Padrón for under-registration and timing. It is the official INE series for rate denominators. Numbers may differ slightly from raw Padrón counts (table 9663 etc).
- **Post-2021 methodology change.** INE switched to the new Censo Anual de Población (administrative-records based) in 2021. 56934 reconciles old/new methodologies; we treat the full 2000–2025 series as comparable, but ±0.5% level-shift artefacts cannot be ruled out around 2020–2022.
- **Open-ended top group.** "95+" pools ages 95 to 100+. Within-bin age structure shifts over time (population is ageing) but rates published in this file are bin-level, not age-specific within 95+.
- **Sex categories.** INE uses binary (Hombres/Mujeres); no non-binary breakdown available.
