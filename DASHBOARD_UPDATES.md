# Dashboard Updates — Embedded Source Hyperlinks

## Summary

The `docs/index.html` dashboard now includes **direct clickable hyperlinks** embedded in each chart's description, pointing to the original sources. No separate data viewer—just one-click access to verification documents.

---

## What Changed

### Before
- Chart descriptions mentioned sources but no links
- Users had to search manually for source documents
- Example: "Official count from Delegación del Gobierno registry"

### After
- All source references are now **clickable hyperlinks 🔗**
- Click → jumps directly to the PDF, table, or official page
- Example: "Official count from [Delegación del Gobierno registry](link)" 

---

## Updated Charts with Embedded Links

### 1. Femicides (Intimate Partner)
Links:
- 🔗 [Delegación del Gobierno registry](https://violenciagenero.igualdad.gob.es/violenciaencifras/victimasmortales/fichamujeres/)
- 🔗 [INE MNP series](https://www.ine.es/jaxiT3/Tabla.htm?t=7947)
- 🔗 [Primary PDF fichas](https://violenciagenero.igualdad.gob.es/violenciaencifras/victimasmortales/fichamujeres/)

### 2. Total Sexual Crimes Reported
Links:
- 🔗 [MIR](https://www.interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/informe-sobre-delitos-contra-la-libertad-e-indemnidad-sexual-en-espana/)
- 🔗 [LO 10/2022 (Solo sí es sí)](https://www.boe.es/diario_oficial/pdf/BOE-A-2022-14630.pdf) — law text explaining the 2022 break

### 3. Rape (Agresión con Penetración) — B6 Issue
Links:
- 🔗 [MIR Anuario headline](https://www.interior.gob.es/opencms/es/archivos-y-documentacion/documentacion-y-publicaciones/publicaciones/publicaciones-descargables/publicaciones-periodicas-anuarios-y-revistas/anuario-estadistico-del-ministerio-del-interior/) (~5,000/yr)
- 🔗 [Informe subcategory](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf) (~1,200/yr) — shows the B6 discrepancy

### 4. Macroencuesta Prevalence
Links to all three waves:
- 🔗 [2015 wave](https://violenciagenero.igualdad.gob.es/violenciaencifras/estudios/colecciones/libro-22-macroencuesta/)
- 🔗 [2019 wave](https://violenciagenero.igualdad.gob.es/violenciaencifras/macroencuesta2015/Macroencuesta2019/home.htm)
- 🔗 [2024 wave](https://violenciagenero.igualdad.gob.es/violenciaEncifras/macroencuesta2024/)

### 5–7. Victim/Perpetrator Profile 2024
Links:
- 🔗 [MIR Informe 2024](https://www.interior.gob.es/opencms/export/sites/default/.galleries/galeria-de-prensa/documentos-y-multimedia/balances-e-informes/2024/Informe_DelitosSexuales24_v111225_ACC.pdf) — appears on all three charts

### 8. Femicide Victims by Nationality
Links:
- 🔗 [Delegación del Gobierno 2024](https://violenciagenero.igualdad.gob.es/violenciaencifras/victimasmortales/fichamujeres/)

---

## How to Use for Verification

1. Open `docs/index.html` in browser
2. Read any chart description
3. **Click any blue underlined link** to jump to source
4. Verify the data matches
5. No modal, no table view—just direct navigation

---

## Link Styling

Links appear as:
- **Blue text** with underline (accent color: #7c83ff)
- **Hover effect:** Background highlight + white text
- **Target:** `_blank` so original dashboard stays open

```css
.chart-sub a, .caveats a {
  color: var(--accent);
  border-bottom: 1px solid var(--accent);
  text-decoration: none;
}

.chart-sub a:hover, .caveats a:hover {
  color: #fff;
  background: rgba(124,131,255,0.1);
  padding: 2px 4px;
  border-radius: 2px;
}
```

---

## Sources Linked

| Source | Type | Coverage |
|---|---|---|
| **Delegación del Gobierno** | Official registry + surveys | Femicide 2003–2024, Macroencuesta 2015/2019/2024 |
| **MIR Anuario** | Police-reported crimes | Sexual crimes 2000–2021 |
| **MIR Informe** | Annual reports | Sexual crimes 2019–2024 (published 2020–2025) |
| **INE MNP** | Mortality by cause | Female homicides 2000–2024 |
| **INE Table 7947** | ECM cause-of-death data | All mortality 2000–2024 |
| **BOE** | Law text | LO 10/2022 (Solo sí es sí) definition change |

---

## Next Steps

1. Open the dashboard and test a few links
2. For sexual violence verification, click sources and cross-check 2024 numbers:
   - Total sexual crimes: should match MIR Informe 2024 Table 1
   - Victim breakdowns: should match MIR Informe 2024 Tables 2–3
3. For femicide: verify against Delegación del Gobierno official registry
4. For Macroencuesta: verify prevalence % against survey reports

All links are **permanent** — they point to official government PDFs and data tables that won't move.
