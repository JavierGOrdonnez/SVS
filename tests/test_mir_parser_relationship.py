"""Tests for the "relación víctima/autor" table extraction (T98).

Fixture text blocks are literal `page.extract_text()` output from the
source PDFs (data/sources/MIR_Informe_DelitosSexuales*.pdf), covering the
three observed on-page formats:
  - 2017: raw counts (MASC/FEM/DESCON/TOTAL), one stray duplicate trailing
    token per leaf row (a chart-legend bleed, ignored).
  - 2018-2023: same 4-column layout, but percentages (2022 used here).
  - 2024: "LABEL COUNT PCT%" -- no sex split in this particular table
    (page also contains an unrelated sex-split bar-chart legend with its
    own MASCULINO/FEMENINO text, which the extractor must not confuse for
    this table's own header).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.mir_parser import parse_relationship_rows


TEXT_2017 = """RELACIÓN VÍCTIMA / AUTOR MASCULINO FEMENINO DESCONOCIDO TOTAL
Violencia género / pareja 12 361 0 373
Cónyuge 0 33 0 33 0
Pareja 9 138 0 147 9
Expareja 3 173 0 176 3
Separado/divorciado 0 17 0 17 0
Violencia familiar exc. VdG y pareja 120 610 0 730
Padre/Madre 12 98 0 110 12
Hijo/Hija 51 210 0 261 51
Resto violencia familiar 57 302 0 359 57
Otras relaciones 212 1.258 3 1.473
Conocido/vecindad 16 106 0 122 16
Amistad 61 341 0 402 61
Laboral/comercial 5 169 0 174 5
Escolar 39 72 1 112 39
Otra relación 91 570 2 663 91
Ninguna / Desconocida 1.147 5.789 25 6.961 1147
1.491 8.018 28 9.537"""

TEXT_2022 = """RELACIÓN VICTIMIZACIÓN / AUTOR MASCULINO FEMENINO DESCONOCIDO TOTAL
Violencia género / pareja 0,1% 4,1% 0,0% 4,2%
Cónyuge 0,0% 0,4% 0,0% 0,4%
Pareja 0,0% 1,6% 0,0% 1,6%
Expareja 0,0% 2,1% 0,0% 2,1%
Separado/divorciado 0,0% 0,1% 0,0% 0,1%
Violencia familiar exc. VdG y pareja 1,0% 6,0% 0,0% 7,0%
Padre/Madre 0,2% 0,7% 0,0% 0,8%
Hijo/Hija 0,4% 2,2% 0,0% 2,6%
Resto  violencia familiar 0,4% 3,1% 0,0% 3,6%
Otras relaciones 1,8% 12,5% 0,0% 14,3%
Conocido/vecindad 0,1% 0,7% 0,0% 0,8%
Amistad 0,4% 3,3% 0,0% 3,7%
Laboral/comercial 0,1% 1,7% 0,0% 1,8%
Escolar 0,2% 1,0% 0,0% 1,2%
Otra relación 0,9% 5,8% 0,0% 6,7%
Ninguna / Desconocida 11,4% 63,0% 0,1% 74,5%"""

# 2024's page also contains an unrelated bar-chart legend with its own
# MASCULINO/FEMENINO/NO CONSTA text -- included here to guard against the
# extractor mistaking that for this table's header.
TEXT_2024 = """4.3. CARACTERÍSTICAS DE LAS VICTIMIZACIONES: RELACIÓN VÍCTIMA/AUTOR
Tipo de relación víctima/autor  2024  %
Violencia de género/en la pareja 1.137 5 %
Cónyuge 90 0,40 %
Pareja 431 1,89 %
Expareja 588 2,59 %
Separado/divorciado 28 0,12 %
Violencia en el ámbito doméstico 1.242 5,72 %
Progenitores 109 0,48 %
Hijo e hija 479 2,11 %
Otras relaciones familiares 712 3,13 %
Otro tipo de relaciones 3.469 14,72 %
Conocido/vecindad 198 0,87 %
Amistad 880 3,86 %
Laboral/comercial 492 2,16 %
Escolar 301 1,32 %
Otra relación 1.482 6,51 %
Relación desconocida 16.930 74,56 % 0,06 %
Total victimizaciones 22.778 100,00 %   FEMENINO        MASCULINO        NO CONSTA
97,5 4 % 2 ,46 %"""


def _find(rows, key):
    matches = [r for r in rows if r["key"] == key]
    assert len(matches) == 1, f"expected exactly one {key!r} row, got {matches}"
    return matches[0]


def test_2017_raw_counts_ignores_stray_trailing_token():
    rows = parse_relationship_rows(TEXT_2017)
    pareja = _find(rows, "pareja")
    assert pareja["count"] == 147
    assert pareja["pct"] is None or abs(pareja["pct"] - 147 / 9537 * 100) < 0.01


def test_2017_group_totals_derive_pct_from_counts_and_sum_to_100():
    rows = parse_relationship_rows(TEXT_2017)
    groups = [r for r in rows if r["is_group_total"]]
    assert len(groups) == 4
    assert abs(sum(r["pct"] for r in groups) - 100.0) < 0.05
    desconocida = _find(rows, "relacion_desconocida")
    assert desconocida["count"] == 6961


def test_2022_percentages_all_16_rows_extracted():
    rows = parse_relationship_rows(TEXT_2022)
    assert len(rows) == 16
    expareja = _find(rows, "expareja")
    assert (expareja["male_pct"], expareja["female_pct"], expareja["unknown_pct"], expareja["pct"]) == (0.0, 2.1, 0.0, 2.1)


def test_2022_group_totals_sum_to_100():
    rows = parse_relationship_rows(TEXT_2022)
    groups = [r for r in rows if r["is_group_total"]]
    assert len(groups) == 4
    assert abs(sum(r["pct"] for r in groups) - 100.0) < 0.05


def test_2024_count_and_pct_not_confused_by_unrelated_chart_legend():
    rows = parse_relationship_rows(TEXT_2024)
    assert len(rows) == 16
    desconocida = _find(rows, "relacion_desconocida")
    # the stray "0,06 %" bleeding in from the age-breakdown chart on the
    # same page must not be picked up as this row's own count/pct.
    assert (desconocida["count"], desconocida["pct"]) == (16930, 74.56)


def test_2024_leaf_row_otras_relaciones_familiares_not_confused_with_group_total():
    rows = parse_relationship_rows(TEXT_2024)
    leaf = _find(rows, "resto_familiar")
    assert leaf["is_group_total"] is False
    assert (leaf["count"], leaf["pct"]) == (712, 3.13)
    group = _find(rows, "otras_relaciones")
    assert group["is_group_total"] is True
    assert (group["count"], group["pct"]) == (3469, 14.72)


def test_2024_group_totals_sum_to_100():
    rows = parse_relationship_rows(TEXT_2024)
    groups = [r for r in rows if r["is_group_total"]]
    assert len(groups) == 4
    assert abs(sum(r["pct"] for r in groups) - 100.0) < 0.05


def test_empty_text_produces_no_rows():
    assert parse_relationship_rows("") == []
    assert parse_relationship_rows("nothing relevant here") == []
