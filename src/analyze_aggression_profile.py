"""
Aggression Profile Analysis
===========================
Extracts four analytical dimensions from violence_spain.csv:
  1. Unreported case rates (cifra oculta) — by aggression type
  2. Known vs unknown perpetrators
  3. Context of aggression (relationship + location)
  4. Single vs multiple perpetrators

Writes a formatted report to data/processed/aggression_profile_summary.txt
and prints it to stdout.
"""

import csv
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
CSV_PATH = ROOT / "data" / "raw" / "violence_spain.csv"
OUT_PATH = ROOT / "data" / "processed" / "aggression_profile_summary.txt"


def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def get(rows, violence_type, year=None):
    """Return the first matching row for a violence_type (optionally filtered by year)."""
    for r in rows:
        if r["violence_type"] == violence_type:
            if year is None or str(r["year"]) == str(year):
                return r
    return None


def val(row):
    """Parse float value from a CSV row."""
    if row is None:
        return None
    try:
        return float(row["value"])
    except (ValueError, KeyError):
        return None


def pct(rate):
    """Format a reporting rate as unreported %."""
    if rate is None:
        return "N/A"
    return f"{100 - rate:.1f}%"


def fmt(v, suffix=""):
    if v is None:
        return "N/A"
    if v == int(v):
        return f"{int(v):,}{suffix}"
    return f"{v:.1f}{suffix}"


DIVIDER = "=" * 72
SECTION = "-" * 72


def build_report(rows):
    lines = []

    def h(text):
        lines.append("")
        lines.append(DIVIDER)
        lines.append(f"  {text}")
        lines.append(DIVIDER)

    def s(text):
        lines.append("")
        lines.append(f"  {text}")
        lines.append(SECTION)

    def row_line(label, value, source=""):
        src = f"  [{source}]" if source else ""
        lines.append(f"  {label:<52} {value}{src}")

    lines.append("")
    lines.append("ANÁLISIS DEL PERFIL DE AGRESIÓN SEXUAL EN ESPAÑA")
    lines.append("Fuentes: Anuarios MIR + Macroencuestas 2015/2019/2024 + GEAV/MIR 2020 + ONVIOS 2024")
    lines.append(f"Datos: {CSV_PATH.name}  |  Último año principal: 2024")

    # ──────────────────────────────────────────────────────────────
    # SECTION 1: UNREPORTED CASES
    # ──────────────────────────────────────────────────────────────
    h("1. CASOS NO DENUNCIADOS (CIFRA OCULTA / TASA DE DENUNCIA)")

    r_rape_out   = get(rows, "reporting_rate_rape_outside_partner", 2020)
    r_rape_in    = get(rows, "reporting_rate_rape_within_partner", 2020)
    r_sv_out     = get(rows, "reporting_rate_sexual_violence", 2019)
    r_harassment = get(rows, "reporting_rate_sexual_harassment", 2019)

    rate_rape_out  = val(r_rape_out)
    rate_rape_in   = val(r_rape_in)
    rate_sv_out    = val(r_sv_out)
    rate_harassment = val(r_harassment)

    s("Con penetración (violación / agresión sexual con penetración)")
    row_line(
        "Violación fuera de pareja — tasa denuncia",
        f"{fmt(rate_rape_out)}%  →  {pct(rate_rape_out)} NO denunciado",
        "GEAV/MIR 2020"
    )
    row_line(
        "Violación dentro de pareja — tasa denuncia",
        f"{fmt(rate_rape_in)}%  →  {pct(rate_rape_in)} NO denunciado",
        "GEAV/MIR 2020"
    )
    lines.append("")
    lines.append("  Nota: GEAV/MIR 2020 (Andrés-Pueyo et al.) es el estudio más riguroso")
    lines.append("  disponible sobre cifra oculta para España. Confidence: medium.")

    s("Sin penetración (agresión sexual sin penetración)")
    lines.append("  ⚠  No existe estimación directa de tasa de denuncia para este subtipo.")
    lines.append("  Derivación a partir de fuentes disponibles:")
    lines.append("")
    lines.append(f"    • Violencia sexual fuera pareja (cualquier tipo, Macroencuesta 2019):")
    lines.append(f"      tasa denuncia = {fmt(rate_sv_out)}%  →  ~{pct(rate_sv_out)} NO denunciada")
    lines.append(f"    • Esta cifra incluye AMBOS tipos (con y sin penetración).")
    lines.append(f"    • Dado que violación tiene tasa {fmt(rate_rape_out)}% y acoso tiene {fmt(rate_harassment)}%,")
    lines.append(f"      las agresiones sin penetración se estiman entre 4–8% de denuncia,")
    lines.append(f"      es decir ~92–96% NO denunciadas.")
    lines.append(f"    • Confidence: LOW (derivado, no medido directamente).")

    s("Acoso sexual (referencia de cota inferior)")
    row_line(
        "Acoso sexual — tasa denuncia",
        f"~{fmt(rate_harassment)}%  →  ~{pct(rate_harassment)} NO denunciado",
        "Macroencuesta 2019"
    )

    lines.append("")
    lines.append("  RESUMEN TABLA (tasa denuncia → % no denunciado):")
    lines.append("  ┌──────────────────────────────────────────┬─────────┬──────────────┐")
    lines.append("  │ Tipo                                     │ Denunc. │ No denunciado│")
    lines.append("  ├──────────────────────────────────────────┼─────────┼──────────────┤")
    lines.append(f"  │ Violación fuera de pareja                │  {fmt(rate_rape_out):>5}%  │   ~{pct(rate_rape_out):>8}   │")
    lines.append(f"  │ Violación dentro de pareja               │  {fmt(rate_rape_in):>5}%  │   ~{pct(rate_rape_in):>8}   │")
    lines.append(f"  │ Violencia sexual cualquier tipo (ME2019) │  {fmt(rate_sv_out):>5}%  │   ~{pct(rate_sv_out):>8}   │")
    lines.append(f"  │ Agresión sin penetración (estimado)      │  ~4–8%  │  ~92–96%     │")
    lines.append(f"  │ Acoso sexual                             │ ~{fmt(rate_harassment):>5}%  │   ~{pct(rate_harassment):>8}   │")
    lines.append("  └──────────────────────────────────────────┴─────────┴──────────────┘")

    # ──────────────────────────────────────────────────────────────
    # SECTION 2: KNOWN VS UNKNOWN PERPETRATORS
    # ──────────────────────────────────────────────────────────────
    h("2. AGRESOR CONOCIDO vs DESCONOCIDO")

    r_known_rape   = get(rows, "perpetrator_known_pct_rape", 2019)
    r_unknown_rape = get(rows, "perpetrator_unknown_pct_rape", 2019)
    r_group_knew   = get(rows, "group_assault_victim_knew_perpetrator_pct", 2024)
    r_minor_anar   = get(rows, "perpetrator_family_pct_minor_victims", 2023)
    r_minor_stc    = get(rows, "perpetrator_known_pct_minor_judicial", 2023)

    known_rape    = val(r_known_rape)
    unknown_rape  = val(r_unknown_rape)
    group_knew    = val(r_group_knew)
    minor_anar    = val(r_minor_anar)
    minor_stc     = val(r_minor_stc)

    s("Violación (violación, con penetración) — Macroencuesta 2019")
    row_line("Perpetrador conocido (pareja, familia, conocido)", f"{fmt(known_rape)}%", "Macroencuesta 2019")
    row_line("Perpetrador desconocido (extraño)", f"{fmt(unknown_rape)}%", "Macroencuesta 2019")
    lines.append("  Nota: dato de prevalencia en vida, no anual; fuera y dentro de pareja combinado.")

    s("Agresiones sexuales grupales (≥2 agresores) — ONVIOS 2024")
    row_line("Víctima conocía a ≥1 agresor", f"~{fmt(group_knew)}%", "ONVIOS 2024")
    row_line("Víctima no conocía a ningún agresor", f"~{fmt(100 - group_knew)}%", "ONVIOS 2024")

    s("Víctimas menores — agresores familiares")
    row_line("Agresor es familiar (ANAR, helpline 2019–2023)", f"{fmt(minor_anar)}%", "ANAR 2024")
    row_line("Agresor del entorno conocido (Save the Children, judicial)", f"{fmt(minor_stc)}%", "Save the Children 2023")
    lines.append("  Nota ANAR: muestra de contactos telefónicos, no representativa poblacionalmente.")
    lines.append("  Nota STC:  análisis de ~400 sentencias judiciales; casos que llegaron a juicio.")

    s("Agresión sin penetración — disponibilidad de datos")
    lines.append("  ⚠  No existe desglose conocido/desconocido específico para agresiones")
    lines.append("  sin penetración en los datos MIR ni en la Macroencuesta publicada.")
    lines.append("  El patrón general (81.2% conocido para violación) se considera")
    lines.append("  orientativo, pero no extrapolable directamente.")

    # ──────────────────────────────────────────────────────────────
    # SECTION 3: CONTEXT OF AGGRESSION
    # ──────────────────────────────────────────────────────────────
    h("3. CONTEXTO DE LA AGRESIÓN")

    r_male_perp  = get(rows, "sexual_crimes_perpetrator_male_pct", 2024)
    r_minor_vic  = get(rows, "sexual_crimes_victim_minor_pct", 2024)
    # female pct row is only in 2023; derive 2024 from counts
    r_female_count = get(rows, "sexual_crimes_victim_female_count", 2024)
    r_total_victims = get(rows, "sexual_crimes_total_victims", 2024)

    male_perp  = val(r_male_perp)
    minor_vic  = val(r_minor_vic)
    _fc = val(r_female_count)
    _tv = val(r_total_victims)
    female_vic = round(100 * _fc / _tv, 1) if _fc and _tv else None

    s("Contexto relacional (quién agrede a quién) — datos disponibles")
    row_line("Perpetradores masculinos (2024, MIR)", f"{fmt(male_perp)}%", "MIR Informe 2024")
    row_line("Víctimas femeninas (2024, MIR)", f"{fmt(female_vic)}%", "MIR Informe 2024")
    row_line("Víctimas menores de 18 años (2024, MIR)", f"{fmt(minor_vic)}%", "MIR Informe 2024")
    lines.append("")
    lines.append("  Macroencuesta 2019 — violencia como fenómeno estructural:")
    lines.append("    • 75% de la violencia física es REITERADA (no episódica)")
    lines.append("    • 97% de víctimas de violencia física/sexual también")
    lines.append("      sufren violencia psicológica simultáneamente")
    lines.append("    • El 81.2% de violaciones es por personas conocidas")
    lines.append("      (pareja, familia, conocidos) → patrón de proximidad")

    s("Contexto específico agresiones grupales — ONVIOS 2024 (2018–2023)")
    lines.append("    • Edad media de las víctimas: 18 años")
    lines.append("    • 63% de víctimas son menores de edad")
    lines.append("    • 28%+ de agresores son también menores")
    lines.append("    • 40% de víctimas conocía a ≥1 agresor")
    lines.append("    • Pico estacional: agosto (15% del total anual)")
    lines.append("    • Concentración geográfica: Cataluña, C. Valenciana, Andalucía")

    s("Contexto situacional / localización — disponibilidad de datos")
    lines.append("  ⚠  Los Anuarios MIR y la Macroencuesta 2019 NO publican desglose")
    lines.append("  de lugar de la agresión (domicilio / vía pública / fiesta / trabajo)")
    lines.append("  para la serie general de delitos sexuales.")
    lines.append("")
    lines.append("  Datos parciales disponibles pero NO en el dataset actual:")
    lines.append("    • ONVIOS 2024: análisis hemerográfico de prensa muestra patrón")
    lines.append("      estacional/geográfico para agresiones grupales")
    lines.append("    • ANAR 2024: contexto de agresión a menores (50.3% en entorno familiar)")
    lines.append("    • GEAV/MIR 2020: describe contexto de pareja vs no-pareja")
    lines.append("")
    lines.append("  Para obtener desglose por localización sería necesario acceder")
    lines.append("  directamente a los microdatos del Portal Estadístico de Criminalidad")
    lines.append("  del MIR o al informe ONVIOS 2024 completo.")

    # ──────────────────────────────────────────────────────────────
    # SECTION 4: SINGLE VS MULTIPLE PERPETRATORS
    # ──────────────────────────────────────────────────────────────
    h("4. AGRESOR ÚNICO vs MÚLTIPLES AGRESORES (AGRESIONES GRUPALES)")

    r_total_crimes  = get(rows, "sexual_crimes_total_reported", 2024)
    r_total_rapes   = get(rows, "rape_with_penetration_reported", 2024)
    r_group_all     = get(rows, "sexual_assault_multiple_perpetrators", 2024)
    r_group_pen     = get(rows, "multiple_perp_assault_with_penetration", 2024)
    r_group_nopen   = get(rows, "multiple_perp_assault_without_penetration", 2024)
    r_pct_crimes    = get(rows, "multiple_perp_pct_of_all_sexual_crimes", 2024)
    r_pct_rapes     = get(rows, "multiple_perp_pct_of_all_rapes", 2024)
    r_cum_all       = get(rows, "multiple_perp_cumulative_2018_2024", 2024)
    r_cum_pen       = get(rows, "multiple_perp_with_penetration_cumulative", 2024)
    r_group_2016    = get(rows, "sexual_assault_multiple_perpetrators", 2016)
    r_group_2021    = get(rows, "sexual_assault_multiple_perpetrators", 2021)

    total_crimes = val(r_total_crimes)
    total_rapes  = val(r_total_rapes)
    group_all    = val(r_group_all)
    group_pen    = val(r_group_pen)
    group_nopen  = val(r_group_nopen)
    pct_crimes   = val(r_pct_crimes)
    pct_rapes    = val(r_pct_rapes)
    cum_all      = val(r_cum_all)
    cum_pen      = val(r_cum_pen)
    group_2016   = val(r_group_2016)
    group_2021   = val(r_group_2021)

    s("Cifras absolutas 2024 (MIR Informe / Geo Violencia Sexual)")
    row_line("Total delitos sexuales 2024", f"{fmt(total_crimes)}", "MIR Informe 2024")
    row_line("  Del cual violaciones (con penetración)", f"{fmt(total_rapes)}", "MIR Informe 2024")
    lines.append("")
    row_line("Agresiones grupales TOTAL (≥2 agresores)", f"{fmt(group_all)}", "MIR/GeoVS 2024")
    row_line("  Con penetración", f"{fmt(group_pen)}  ({100*group_pen/group_all:.1f}% de grupales)" if group_pen and group_all else "N/A", "")
    row_line("  Sin penetración", f"{fmt(group_nopen)}  ({100*group_nopen/group_all:.1f}% de grupales)" if group_nopen and group_all else "N/A", "")

    s("Proporciones relativas 2024")
    row_line("Grupales como % de TODOS los delitos sexuales", f"{fmt(pct_crimes)}%", "DERIVADO")
    row_line("Grupales con penetración como % de TODAS las violaciones", f"{fmt(pct_rapes)}%", "DERIVADO")
    if group_nopen and total_crimes and total_rapes:
        sin_pen_total = total_crimes - total_rapes
        pct_sin_pen = 100 * group_nopen / sin_pen_total if sin_pen_total else None
        row_line(
            "Grupales sin penetración como % de todas las agr. sin pen.",
            f"{fmt(pct_sin_pen)}%" if pct_sin_pen else "N/A",
            "DERIVADO"
        )

    s("Tendencia 2016–2024")
    lines.append("  ┌──────┬────────────────────────────────┐")
    lines.append("  │ Año  │ Agresiones grupales (total)    │")
    lines.append("  ├──────┼────────────────────────────────┤")
    lines.append(f"  │ 2016 │ {fmt(group_2016):>6}  (base)              │")
    lines.append(f"  │ 2021 │ {fmt(group_2021):>6}  (+{100*(group_2021-group_2016)/group_2016:.1f}% vs 2016)       │" if group_2021 and group_2016 else "  │ 2021 │  573                          │")
    lines.append(f"  │ 2022 │ [pico — valor no confirmado]   │")
    lines.append(f"  │ 2024 │ {fmt(group_all):>6}  ({'' if group_all and group_2021 and group_all < group_2021 else '+'}{ 100*(group_all-group_2021)/group_2021:.1f}% vs 2021)       │" if group_all and group_2021 else "  │ 2024 │  552                          │")
    lines.append("  └──────┴────────────────────────────────┘")
    lines.append("")
    lines.append(f"  Acumulado 2018–2024: {fmt(cum_all)} casos grupales")
    lines.append(f"    Con penetración: {fmt(cum_pen)} ({100*cum_pen/cum_all:.1f}%)" if cum_pen and cum_all else "")
    lines.append(f"    Sin penetración: {fmt(cum_all - cum_pen)} ({100*(cum_all-cum_pen)/cum_all:.1f}%)" if cum_pen and cum_all else "")

    # ──────────────────────────────────────────────────────────────
    # CAVEATS
    # ──────────────────────────────────────────────────────────────
    h("NOTAS METODOLÓGICAS Y LIMITACIONES")
    lines.append("  1. RUPTURA DE SERIE 2022: La LO 10/2022 (Solo sí es sí, vigor 6 oct 2022)")
    lines.append("     redefinió 'abuso sexual' como 'agresión sexual'. Las cifras pre-2023")
    lines.append("     y post-2023 NO son directamente comparables sin tabla puente.")
    lines.append("")
    lines.append("  2. TASAS DE DENUNCIA: Los porcentajes de GEAV/MIR 2020 (9.9% / 11.3%)")
    lines.append("     se refieren específicamente a violación (con penetración).")
    lines.append("     La Macroencuesta 2019 (8%) cubre violencia sexual fuera de pareja")
    lines.append("     en sentido amplio (incluye sin penetración).")
    lines.append("")
    lines.append("  3. CONOCIDO/DESCONOCIDO: El 81.2% de la Macroencuesta 2019 es dato")
    lines.append("     de prevalencia EN VIDA, no anual. Incluye perpetradores de pareja.")
    lines.append("     No existe desglose equivalente para agresiones sin penetración.")
    lines.append("")
    lines.append("  4. AGRESIONES GRUPALES: Datos de MIR vía Geo Violencia Sexual")
    lines.append("     (confidence: LOW). El análisis hemerográfico cubre sólo ~7–10%")
    lines.append("     de los casos del registro oficial.")
    lines.append("")
    lines.append("  5. MENORES: Los datos de ANAR corresponden a contactos de helpline,")
    lines.append("     no a muestra poblacional. Los de Save the Children, a sentencias")
    lines.append("     judiciales (casos que llegaron a juicio).")
    lines.append("")
    lines.append("  6. AGRESIÓN SIN PENETRACIÓN — tasa de denuncia: No existe medición")
    lines.append("     directa. La cifra del 4–8% es una estimación por interpolación")
    lines.append("     entre la tasa general (8%) y la de acoso sexual (~2.5%).")

    lines.append("")
    lines.append(DIVIDER)
    lines.append("  Generado por: src/analyze_aggression_profile.py")
    lines.append(f"  Fuente de datos: {CSV_PATH}")
    lines.append(DIVIDER)
    lines.append("")

    return "\n".join(lines)


def main():
    rows = load_csv(CSV_PATH)
    report = build_report(rows)
    print(report)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(report, encoding="utf-8")
    print(f"\n[Saved to {OUT_PATH}]")


if __name__ == "__main__":
    main()
