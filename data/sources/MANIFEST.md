# Reference Documents — Sexual Violence & Femicide Analysis

Downloaded 2026-05-24 for supplementary analysis and methodological review.

## Documents

| File | Size | Date | Source | Description |
|------|------|------|--------|---|
| MIR_SexualViolence_Synthesis.pdf | 4.1M | 2024 | Ministerio del Interior | Estudio sobre la violencia sexual en España — Una síntesis estimativa. Comprehensive synthesis of sexual violence data across all MIR sources. |
| CCOO_Analysis.pdf | 1.6M | Unknown | CCOO (Spanish trade union) | Union analysis report on sexual violence and labor sector impacts. |
| MIR_ViolenceWomen_2015-2019.pdf | 12M | 2020 | Ministerio del Interior | Informe sobre violencia contra la mujer 2015–2019. Comprehensive 5-year report with victim/perpetrator demographics, regional data, and temporal trends. |
| MIR_GroupSexualViolence_2023.pdf | 4.2M | 2023-10-25 | Ministerio del Interior | Informe sobre violencia sexual en grupo (group sexual violence). Specialized analysis of gang rape and coordinated sexual assaults. |

## Usage Notes

- **Do not cite directly in main analysis** — Use only for methodology verification and additional context
- **Intended for future extraction** — These reports contain rich demographic/regional data suitable for Python parsing in T18–T23
- **Superseded by official MIR Informe/Anuario** — Where conflicts arise between synthesis reports and primary sources, trust primary MIR publications
- **Format variability** — Reports use different table layouts; parser development (T21) must account for format heterogeneity

## Next Steps

- Review each document for extractable tables
- Identify demographic/regional/temporal breakdown patterns
- Plan Python parser structure (T21) based on actual table formats in these PDFs
