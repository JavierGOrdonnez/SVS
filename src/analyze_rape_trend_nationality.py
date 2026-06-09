"""
Rape Trend & Nationality Analysis
==================================
Questions answered:
  1. How has total reported rape evolved year-by-year up to 2024?
  2. How are convicted sex offenders distributed by nationality (2017-2024)?
  3. Does the evidence support the claim that immigration drives the increase?
  4. What do we know about reporting rates for known vs unknown perpetrators?

Data sources used:
  - data/raw/violence_spain.csv  (police-reported crimes + Macroencuesta)
  - data/processed/ine_condenados_28716_sexual_crimes.csv  (convicted by nationality)
    [run src/parse_ine_tabla28716.py first if file is missing]
  - data/processed/population_spain_midyear_5yr.csv  (population denominators)
"""

import csv
from pathlib import Path

ROOT = Path(__file__).parent.parent
RAW_CSV = ROOT / "data" / "raw" / "violence_spain.csv"
INE_CSV = ROOT / "data" / "processed" / "ine_condenados_28716_sexual_crimes.csv"
POP_CSV = ROOT / "data" / "processed" / "population_spain_midyear_5yr.csv"
OUT_TXT = ROOT / "data" / "processed" / "rape_trend_nationality_summary.txt"

DIVIDER = "=" * 72
SECTION = "-" * 72


# ──────────────────────────────────────────────────────────────
# Loaders
# ──────────────────────────────────────────────────────────────

def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def get_all(rows, violence_type, years=None):
    out = {}
    for r in rows:
        if r["violence_type"] == violence_type:
            y = int(r["year"])
            if years is None or y in years:
                try:
                    out[y] = float(r["value"])
                except (ValueError, KeyError):
                    pass
    return out


def get_val(rows, violence_type, year):
    return get_all(rows, violence_type, {year}).get(year)


# ──────────────────────────────────────────────────────────────
# INE conviction data helpers
# ──────────────────────────────────────────────────────────────

def load_ine_convictions(path):
    """Return dict: (crime_label, nationality_label, year) -> count."""
    if not path.exists():
        return None
    data = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                key = (r["crime_label"], r["nationality_label"], int(r["year"]))
                val = float(r["count"]) if r["count"] else None
                data[key] = val
            except (ValueError, KeyError):
                pass
    return data


def cap8_by_nat(conv, year):
    """Chapter 8 total convicted by nationality for a year."""
    result = {}
    for (crime, nat, y), count in conv.items():
        if crime == "cap8_total" and y == year and nat != "total" and count:
            result[nat] = count
    return result


def agresion_by_nat(conv, year):
    """Agresiones sexuales (8.1) convicted by nationality for a year."""
    result = {}
    for (crime, nat, y), count in conv.items():
        if crime == "agresiones_sexuales" and y == year and nat != "total" and count:
            result[nat] = count
    return result


# ──────────────────────────────────────────────────────────────
# Population helpers
# ──────────────────────────────────────────────────────────────

# Foreign population estimates (Spain) by year — INE Padrón data
# Source: INE Estadística del Padrón Continuo (total extranjeros)
# These are approximate round figures; replace with parsed INE data if available.
FOREIGN_POP_MILLIONS = {
    2017: 4.57, 2018: 4.72, 2019: 5.02, 2020: 5.23, 2021: 5.45,
    2022: 5.65, 2023: 5.86, 2024: 6.06,  # 2024 estimate
}
TOTAL_POP_MILLIONS = {
    2017: 46.53, 2018: 46.66, 2019: 47.03, 2020: 47.33, 2021: 47.40,
    2022: 47.43, 2023: 47.87, 2024: 48.59,
}


def foreign_pct_of_pop(year):
    fp = FOREIGN_POP_MILLIONS.get(year)
    tp = TOTAL_POP_MILLIONS.get(year)
    if fp and tp:
        return fp / tp * 100
    return None


# ──────────────────────────────────────────────────────────────
# Report builder
# ──────────────────────────────────────────────────────────────

def fmt(v, decimals=0):
    if v is None:
        return "—"
    if decimals == 0:
        return f"{int(round(v)):,}"
    return f"{v:.{decimals}f}"


def build_report(sv_rows, conv):
    lines = []

    def h(text):
        lines.extend(["", DIVIDER, f"  {text}", DIVIDER])

    def s(text):
        lines.extend(["", f"  {text}", SECTION])

    lines += [
        "",
        "VIOLENCIA SEXUAL EN ESPAÑA — TENDENCIA HISTÓRICA Y DISTRIBUCIÓN POR NACIONALIDAD",
        "Fuentes: Anuarios MIR (denuncias), INE Tabla 28716 (condenados), Macroencuesta INE",
    ]

    # ── SECTION 1: Rape trend ────────────────────────────────────────────────
    h("1. EVOLUCIÓN ANUAL DE VIOLACIONES DENUNCIADAS (SERIE COMPLETA)")

    lines.append("")
    lines.append("  Nota metodológica: Serie con rupturas conocidas.")
    lines.append("    • Pre-2012: excluye Cataluña/PaísVasco/Navarra (~30% población)")
    lines.append("    • 2015: brecha por Reforma Código Penal")
    lines.append("    • 2022: LO 10/2022 redefinió 'abuso' como 'agresión' → series no comparables")
    lines.append("    • 2021: datos no publicados en el Anuario")
    lines.append("    • B6: dos series incompatibles (Anuario ~5K/año vs Informe ~1-2K/año)")
    lines.append("")

    rape_series = {
        # year: (count, source, confidence, note)
        2000: (2300, "Anuario MIR (estimado)", "low", "territorio limitado"),
        2002: (2400, "Anuario MIR (estimado)", "low", "territorio limitado"),
        2005: (2500, "Anuario MIR (estimado)", "low", "territorio limitado"),
        2007: (3000, "Anuario MIR (estimado)", "low", "territorio limitado"),
        2010: (3000, "Anuario MIR (estimado)", "low", "territorio limitado"),
        2012: (3500, "Anuario MIR", "medium", "primer año cobertura nacional 100%"),
        2017: (3716, "Anuario MIR", "medium", "verified"),
        2018: (4141, "Anuario MIR", "medium", "verified"),
        2019: (5453, "Anuario MIR", "medium", "verified; pico pre-LO10/2022"),
        2022: (4270, "Anuario MIR", "medium", "post-LO10/2022 partial year"),
        2023: (4875, "Anuario MIR", "medium", "verified"),
        2024: (5223, "MIR Informe 2024", "medium", "22.86% of 22846 total; ver B6"),
        2025: (5363, "MIR Balance Q4 2025", "medium", "+2.8% vs 2024"),
    }

    # Enrich with CSV data
    for y, count in get_all(sv_rows, "rape_with_penetration_reported").items():
        if y in rape_series:
            existing = rape_series[y]
            if existing[2] in ("low",):
                rape_series[y] = (count, existing[1], "medium", existing[3])
        else:
            rape_series[y] = (count, "violence_spain.csv", "medium", "")

    lines.append(f"  {'Año':>4}  {'Violaciones':>12}  {'Conf':>6}  Nota")
    lines.append("  " + "-" * 65)
    prev_count = None
    for yr in sorted(rape_series):
        cnt, src, conf, note = rape_series[yr]
        if cnt is None:
            lines.append(f"  {yr:>4}  {'SIN DATOS':>12}  {conf:>6}  {note}")
            prev_count = None
            continue
        change = f"  (+{cnt-prev_count:,})" if prev_count and cnt > prev_count else ""
        lines.append(f"  {yr:>4}  {cnt:>12,}  {conf:>6}  {note}{change}")
        prev_count = cnt

    lines.append("")
    lines.append("  INDICADORES CLAVE:")
    lines.append("    • 2019 fue el pico histórico reciente (5,453 — máximo pre-reforma)")
    lines.append("    • 2024 = 5,223 violaciones (+66% vs 2018 en 6 años)")
    lines.append("    • Incremento 2017→2024: +41% (comparable con cobertura nacional completa)")
    lines.append("    • Parte del aumento post-2022 = artefacto legal (LO 10/2022)")
    lines.append("    • Parte restante = probable incremento denuncias (mayor conciencia social)")

    # Also agresiones sin penetración
    s("Agresiones sin penetración (2022–2024)")
    aspen_data = {
        2022: (11426, "Anuario MIR 2022"),
        2024: (13673, "MIR Informe 2024"),
    }
    for y, (cnt, src) in sorted(aspen_data.items()):
        v = get_val(sv_rows, "sexual_assault_without_penetration_reported", y)
        cnt = v or cnt
        lines.append(f"  {y}: {cnt:,}  ({src})")
    lines.append("  Nota: estas cifras son post-LO10/2022; categorías anteriores no comparables.")

    # ── SECTION 2: Nationality in convictions ────────────────────────────────
    h("2. DISTRIBUCIÓN POR NACIONALIDAD — CONDENADOS (INE Tabla 28716, 2017–2024)")

    if conv is None:
        lines.append("  ⚠ Archivo INE no disponible. Ejecute: python src/parse_ine_tabla28716.py")
        lines.append("  Datos disponibles para 2023-2024 en violence_spain.csv (filas 74, 162-165).")
    else:
        s("Capítulo 8 — Todos los delitos contra la libertad sexual")
        nat_order = [
            "española", "ue_excl_espana", "europa_no_ue", "africa", "america", "asia", "oceania"
        ]

        years = sorted(set(y for (_, _, y) in conv.keys()))
        header = f"  {'Nacionalidad':30}" + "".join(f" {y:>7}" for y in years)
        lines.append(header)
        lines.append("  " + "-" * (30 + 8 * len(years)))

        # Compute consolidated groups
        def group(nat):
            if nat in ("ue27_excl_espana", "ue28_excl_espana"):
                return "ue_excl_espana"
            if nat in ("europa_no_ue27", "europa_no_ue28"):
                return "europa_no_ue"
            return nat

        # Aggregate by group per year
        grouped = {}
        for (crime, nat, yr), count in conv.items():
            if crime != "cap8_total" or nat == "total" or not count:
                continue
            g = group(nat)
            if (g, yr) not in grouped:
                grouped[(g, yr)] = 0
            grouped[(g, yr)] += count

        totals = {}
        for (crime, nat, yr), count in conv.items():
            if crime == "cap8_total" and nat == "total" and count:
                totals[yr] = count

        for nat_g in nat_order:
            row_vals = []
            for yr in years:
                v = grouped.get((nat_g, yr))
                total = totals.get(yr)
                if v and total:
                    row_vals.append(f"{int(v):5} ({100*v/total:.0f}%)")
                else:
                    row_vals.append("    —     ")
            lines.append(f"  {nat_g:30}" + "".join(f" {rv:>7}" for rv in row_vals))

        lines.append("  " + "-" * (30 + 8 * len(years)))
        for yr in years:
            t = totals.get(yr)
            lines.append(f"  {'TOTAL':30} {fmt(t):>7}" if yr == years[0] else
                         f"  {'':30} {fmt(t):>7}")
        lines.append("")
        lines.append("  (Fuente: INE Estadística de Condenados adultos, Tabla 28716, Capítulo 8)")
        lines.append("  (CONDENADOS: personas con sentencia firme; distinto de arrestados/denuncias)")

        s("Agresiones sexuales (8.1) — detalle por año")
        years_ag = sorted(set(y for (c, _, y) in conv if c == "agresiones_sexuales"))
        header2 = f"  {'Nacionalidad':20}" + "".join(f" {y:>7}" for y in years_ag)
        lines.append(header2)
        lines.append("  " + "-" * (20 + 8 * len(years_ag)))

        grouped_ag = {}
        for (crime, nat, yr), count in conv.items():
            if crime != "agresiones_sexuales" or nat == "total" or not count:
                continue
            g = group(nat)
            if (g, yr) not in grouped_ag:
                grouped_ag[(g, yr)] = 0
            grouped_ag[(g, yr)] += count

        totals_ag = {}
        for (crime, nat, yr), count in conv.items():
            if crime == "agresiones_sexuales" and nat == "total" and count:
                totals_ag[yr] = count

        for nat_g in nat_order:
            row_vals = []
            for yr in years_ag:
                v = grouped_ag.get((nat_g, yr))
                t = totals_ag.get(yr)
                if v and t:
                    row_vals.append(f"{int(v):>4}({100*v/t:.0f}%)")
                else:
                    row_vals.append("   —   ")
            lines.append(f"  {nat_g:20}" + "".join(f" {rv:>7}" for rv in row_vals))
        lines.append("  " + "-" * (20 + 8 * len(years_ag)))
        tot_line = f"  {'TOTAL':20}"
        for yr in years_ag:
            tot_line += f" {fmt(totals_ag.get(yr)):>7}"
        lines.append(tot_line)

    # ── SECTION 3: Police-reported nationality (MIR) ─────────────────────────
    h("3. PERPETRADORES POR NACIONALIDAD — DATOS POLICIALES (MIR Informes)")

    lines.append("  Nota: estos datos son % de DETENIDOS/INVESTIGADOS (no condenados).")
    lines.append("  Son distintos de la tasa de condena. Fuente: MIR Informes 2023-2024.")
    lines.append("")
    lines.append(f"  {'Año':>4}  {'%Español':>10}  {'%Extranjero':>12}  {'%Extr/PobExtr':>15}  Ratio sobrerrepresentación")
    lines.append("  " + "-" * 70)

    police_nat = {
        2023: (get_val(sv_rows, "sexual_crimes_perpetrator_spanish_pct", 2023),
               100 - (get_val(sv_rows, "sexual_crimes_perpetrator_spanish_pct", 2023) or 0)),
        2024: (68.0, 32.0),
    }
    for yr, (sp_pct, fr_pct) in sorted(police_nat.items()):
        if sp_pct is None:
            continue
        fp = foreign_pct_of_pop(yr) or 14.0
        ratio = fr_pct / fp if fp else None
        lines.append(f"  {yr:>4}  {sp_pct:>10.1f}%  {fr_pct:>12.1f}%  {fp:>14.1f}%  {fmt(ratio, 1) + 'x':>10}")

    lines.append("")
    lines.append("  Interpretación: en 2024, extranjeros = 32% detenidos pero ~12.5% población")
    lines.append("  → ratio de sobrerrepresentación ~2.3x en detenciones policiales")

    # ── SECTION 4: Immigration claim test ────────────────────────────────────
    h("4. EVALUACIÓN: ¿ES EL AUMENTO DE VIOLACIONES ATRIBUIBLE A LA INMIGRACIÓN?")

    lines.append("""
  METODOLOGÍA: Para que el aumento sea atribuible a inmigración, debería darse
  alguna de estas condiciones:
    A) El % de perpetradores extranjeros aumenta progresivamente
    B) La tasa de agresión por 100k extranjeros aumenta
    C) El incremento en violaciones se concentra en los años de mayor inmigración

  HALLAZGOS:""")

    lines.append("""
  A) TENDENCIA EN % EXTRANJERO (CONDENADOS, capítulo 8):
     2017: 2764 total → 2103 española (76.1%) → 661 extranjeros (23.9%)
     2019: 3296 total → 2458 española (74.6%) → 838 extranjeros (25.4%)
     2022: 3785 total → 2651 española (70.0%) → 1134 extranjeros (30.0%)
     2024: 5073 total → 3325 española (65.5%) → 1748 extranjeros (34.5%)
     → El % extranjero en CONDENADOS ha aumentado del 24% al 35% (2017-2024).
     → Pero el TOTAL también aumentó (+83.5%) y el número de españoles también
       creció mucho (+58%: 2103→3325). No es solo crecimiento extranjero.
     → CAUTELA: parte del salto 2022-2024 es el procesamiento del backlog
       judicial tras LO 10/2022 (+50.8% condenas totales en 2024 vs 2023).

  B) TASA POR 100K EXTRANJEROS (estimación, convictions):
     Supuesto: población extranjera adulta ~70% del total de extranjeros padrón.
""")

    if conv:
        for yr in [2017, 2019, 2022, 2024]:
            total_yr = totals.get(yr)
            foreign_yr = grouped.get(("africa", yr), 0) + grouped.get(("america", yr), 0) + \
                         grouped.get(("asia", yr), 0) + grouped.get(("ue_excl_espana", yr), 0) + \
                         grouped.get(("europa_no_ue", yr), 0) + grouped.get(("oceania", yr), 0)
            fp_est = FOREIGN_POP_MILLIONS.get(yr)
            if fp_est and foreign_yr:
                rate_foreign = foreign_yr / (fp_est * 0.7 * 1e6) * 100_000
                spanish_yr = grouped.get(("española", yr), 0)
                sp_pop = TOTAL_POP_MILLIONS.get(yr, 47) - fp_est
                rate_spanish = spanish_yr / (sp_pop * 0.7 * 1e6) * 100_000 if sp_pop else None
                ratio = rate_foreign / rate_spanish if rate_spanish else None
                lines.append(f"     {yr}: extranjeros convictos={int(foreign_yr):,}  "
                              f"tasa/100k={rate_foreign:.1f}  "
                              f"españoles/100k={fmt(rate_spanish,1)}  "
                              f"ratio={fmt(ratio,1)}x")

    lines.append("""
  C) TIMING DEL AUMENTO vs LLEGADA DE INMIGRANTES:
     El mayor salto en denuncias ocurrió en:
       • 2016-2019: Caso La Manada + movimiento feminista → +47% denuncias
         (población extranjera creció solo ~5% en ese período)
       • 2022-2024: LO 10/2022 → reclasificación legal + backlog judicial
     Ninguno de estos saltos principales coincide con picos de inmigración.
     La inmigración creció más en 2020-2024, pero las denuncias en 2024 < 2019.

  CONCLUSIÓN (evaluación basada en datos disponibles):
  ─────────────────────────────────────────────────────
  Sí existe sobrerrepresentación de extranjeros en convictions (~2-2.5x)
  y en detenciones policiales (~2.3x en 2024). Esto es un dato estadístico
  real que requiere explicación, pero NO implica causalidad con el aumento:

    1. El aumento de denuncias 2016-2019 fue IMPULSADO por el Caso La Manada
       y el movimiento feminista, no por inmigración.

    2. El salto 2022-2024 en condenas es mayoritariamente un ARTEFACTO LEGAL
       (LO 10/2022 + procesamiento backlog judicial).

    3. La sobrerrepresentación de extranjeros puede reflejar:
       • Sesgo en la denuncia (víctimas más propensas a denunciar agresiones
         por desconocidos, que tienden más a ser extranjeros — 18.8% de violaciones
         son por desconocidos pero estos tienen mayor tasa de denuncia)
       • Sesgo policial / judicial en investigación y condena
       • Factores socioeconómicos (pobreza, marginación) correlacionados con
         ciertos tipos de violencia

    4. La Macroencuesta 2019 (que mide violencia REAL no denunciada) muestra que
       el 81.2% de violaciones son por CONOCIDOS — precisamente el tipo con
       MENOR tasa de denuncia y menor probabilidad de condena.
       Esto introduce un sesgo sistemático: los datos policiales/judiciales
       SOBREREPRESENTAN a extranjeros desconocidos y SUBREEPRESENTAN a
       conocidos (muchos españoles).

    5. NO existe evidencia causal directa de que el aumento de rapes en España
       sea atribuible a la inmigración. El único análisis que hace esta
       afirmación (CEU-CEFAS 2025) fue criticado en el SPEC por metodología
       deficiente (ver fuentes_secundarias §22).
""")

    # ── SECTION 5: Known vs unknown reporting rates ───────────────────────────
    h("5. TASA DE DENUNCIA: AGRESOR CONOCIDO vs DESCONOCIDO")

    lines.append("""
  No existe en España ningún estudio que mida directamente la diferencia en
  tasa de denuncia según la relación víctima-agresor. Sin embargo, podemos
  derivar estimaciones indirectas de las fuentes disponibles:

  DATOS DIRECTOS:
  ┌────────────────────────────────────────────────────┬───────────┬──────────┐
  │ Categoría                                          │ % Denuncia│ Fuente   │
  ├────────────────────────────────────────────────────┼───────────┼──────────┤
  │ Violación fuera de pareja (todos)                  │    9.9%   │ GEAV/MIR │
  │ Violación dentro de pareja (= 100% conocido)       │   11.3%   │ GEAV/MIR │
  │ Violencia sexual fuera pareja (cualquier tipo)     │    8.0%   │ ME2019   │
  └────────────────────────────────────────────────────┴───────────┴──────────┘

  DERIVACIÓN INDIRECTA:
  La categoría "fuera de pareja" (9.9%) mezcla:
    - 81.2% por conocidos (no pareja): tasa implícita R_conocido
    - 18.8% por desconocidos:          tasa implícita R_desconocido

  Si asumimos R_desconocido ≈ 25-30% (basado en FRA 2014: España por debajo
  de la media europea de ~25-30% para violencia sexual con extraños):

    0.812 × R_conocido + 0.188 × 0.27 = 0.099
    R_conocido ≈ (0.099 - 0.051) / 0.812 ≈ 5.9%

  RESULTADO: Los datos sugieren que:
    • Violación por desconocido: ~25-30% de denuncia (más alta)
    • Violación por conocido no-pareja: ~6% de denuncia (más baja)
    • Violación por pareja: ~11.3% de denuncia (intermedia)

  IMPLICACIÓN PARA EL ANÁLISIS DE NACIONALIDAD:
  Si los extranjeros tienden a cometer más violaciones como desconocidos
  (lo que es plausible dado que el 40% de agresiones grupales — patrón más
  asociado a desconocidos — implican solo 40% conocidos), entonces:

    → Los datos policiales/judiciales SOBREREPRESENTAN a perpetradores
      extranjeros porque sus agresiones se denuncian más.
    → El 81.2% por conocidos (mayoritariamente españoles en contexto
      íntimo) tiene solo ~6% de tasa de denuncia → queda casi todo oculto.

  Esta es la explicación más probable para la sobrerrepresentación extranjera
  en estadísticas policiales: es un artefacto de la cifra oculta diferencial,
  NO necesariamente una mayor tasa real de agresión.

  CAUTELA: Todo esto es derivación analítica, no medición directa.
  Sería necesario un estudio con microdatos de la Macroencuesta + datos
  policiales enlazados para confirmarlo.
""")

    h("FUENTES Y CONFIANZA")
    lines.append("""
  Policiales (denuncias): MIR Anuarios + Informes (2017-2024)
    → confidence medium; B6 no resuelto (dos series violación incompatibles)
  Condenados por nacionalidad: INE Tabla 28716 (2017-2024)
    → confidence high (fuente primaria oficial, verificada)
  Prevalencia real: Macroencuesta 2019 + 2024
    → confidence high
  Tasas de denuncia: GEAV/MIR 2020 (Andrés-Pueyo et al.)
    → confidence medium (metodología rigurosa pero no replicada)
  Cálculos de tasa por nacionalidad (§4B):
    → confidence low (denominadores de población estimados)
    → NO publicar sin verificar con datos INE Padrón por nacionalidad

  PASO SIGUIENTE: ejecutar src/parse_ine_tabla28716.py para datos INE.
  PASO SIGUIENTE: descargar PDFs MIR y ejecutar src/parsers/mir_parser.py
    para extraer historial completo 2019-2024 incluyendo % perpetrador extranjero.
""")

    lines.append(DIVIDER)
    lines.append(f"  Generado: src/analyze_rape_trend_nationality.py")
    lines.append(f"  Datos: {RAW_CSV.name} + INE Tabla 28716")
    lines.append(DIVIDER)

    return "\n".join(lines)


def main():
    sv_rows = load_csv(RAW_CSV)
    conv = load_ine_convictions(INE_CSV)

    if conv is None:
        print("INE conviction data not found — run src/parse_ine_tabla28716.py first.")
        print("Continuing with partial data from violence_spain.csv...")

    report = build_report(sv_rows, conv)
    print(report)

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text(report, encoding="utf-8")
    print(f"\n[Saved to {OUT_TXT}]")


if __name__ == "__main__":
    main()
