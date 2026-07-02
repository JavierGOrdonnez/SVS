"""Tests for per-country nationality breakdown extraction (T26).

Fixture rows are literal slices of pdfplumber's `extract_tables()` output,
captured directly from the source PDFs (data/sources/MIR_Informe_Delitos
Sexuales*.pdf), covering all three observed table-format eras:
  - 2019/2021: '\\n'-joined country-list cell per region, sex columns in
    Masculino/Femenino/Desconocido/Total order, in-table header row.
  - 2022/2023: same as above plus 'Columna*' bleed-through cells and
    '#¡DIV/0!' Excel-error artifacts scattered in region rows.
  - 2024: one flat row per region/country, Femenino/Masculino REVERSED vs.
    earlier years (col_order_hint from page text, no in-table header), and
    perpetrators-table rows with NO sex breakdown at all (total + % only).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.mir_parser import parse_country_breakdown_table, CountryBreakdown


# ── 2019 victims (page 19 of MIR_Informe_DelitosSexuales2019.pdf) ──
ROWS_2019_VICTIMS = [
    [None, None, None, None, None, 'Masculino', None, 'Femenino', None, 'Desconocido', None, 'Total', None, '% sobre total', '', None, None, None],
    [None, '2.1.‐ ÁFRICA', None, None, None, '75', None, '474', None, '1', None, '550', None, '3,5%', '15,3%', 'REJ', '', ''],
    ['', 'Marruecos\nNigeria\nResto', None, None, None, '59\n2\n14', None, '337\n47\n90', None, '1\n0\n0', None, '397\n49\n104', None, '2,5%\n0,3%\n0,7%', '', 'NARTXE', '', ''],
]

# ── 2019 perpetrators (page 31) ──
ROWS_2019_PERPS = [
    [None, None, None, None, None, 'Masculino', None, 'Femenino', None, 'Desconocido', None, 'Total', None, '% sobre total', '', None, None, None],
    [None, '2.1.‐ ÁFRICA', None, None, None, '1.098', None, '12', None, '0', None, '1.110', None, '11,5%', '32,9%', '35,0%', '', ''],
    ['', 'Marruecos\nArgelia\nResto', None, None, None, '744\n94\n260', None, '7\n0\n5', None, '0\n0\n0', None, '751\n94\n265', None, '7,8%\n1,0%\n2,7%', '', 'SOREJN', '', ''],
]

# ── 2022 perpetrators (page 31 of MIR_Informe_DelitosSexuales2022.pdf) --
# includes 'Columna*' bleed-through + doubled-percentage-string noise on the
# unrelated ESPAÑOLES row, which _compact_cells must already strip.
ROWS_2022_PERPS = [
    [None, None, None, None, None, 'Masculino', None, 'Femenino', None, 'Desconocido', None, 'Total', None, '% sobre total', '', '', None, None, None, '', None],
    ['', '1.- ESPAÑOLES', None, None, None, '7.037', None, '479', None, '0', None, '7.516', None, '64,2% 64,2%', '', '', '', None, '', '', ''],
    ['', '2.1.- ÁFRICA', None, None, None, '1.343', None, '30', None, '0', None, '1.373', None, '11,7%', '', '', '', '35,8%\n32,8%', '', '', ''],
    ['', 'Marruecos\nArgelia\nResto', None, None, None, '889\n126\n328', None, '18\n0\n12', None, '0\n0\n0', None, '907\n126\n340', None, '7,8%\n1,1%\n2,9%', '', '', 'S\nO\nR\nE\nJ\nN', '', '', ''],
]

# ── 2024 victims (page 30 of MIR_Informe_DelitosSexuales2024.pdf) --
# flat rows, Femenino before Masculino, hint supplied by caller (as the real
# InformeParser does via _detect_sex_col_order_from_text on the page text).
ROWS_2024_VICTIMS = [
    ['2.1.', 'África', '596', '142', '0', '738', '3,24%'],
    ['', 'Marruecos', '440', '87', '0', '527', '2,31%'],
    ['', 'Argelia', '47', '19', '0', '66', '0,29%'],
]
HINT_2024_VICTIMS = ['female', 'male', 'unknown', 'total']

# ── 2024 perpetrators (page 52) -- no sex breakdown at all, total + % only ──
ROWS_2024_PERPS = [
    ['2.1.', 'África', '1.839', '12,79 %'],
    ['', 'Marruecos', '1.100', '7,65 %'],
    ['', 'Argelia', '241', '1,68 %'],
]


def _find(entries: list[CountryBreakdown], name: str) -> CountryBreakdown:
    matches = [e for e in entries if e.name == name]
    assert len(matches) == 1, f"expected exactly one {name!r} entry, got {matches}"
    return matches[0]


def test_2019_victims_marruecos():
    entries = parse_country_breakdown_table(ROWS_2019_VICTIMS)
    m = _find(entries, "MARRUECOS")
    assert (m.male, m.female, m.unknown, m.total, m.pct) == (59, 337, 1, 397, 2.5)
    assert m.region == "AFRICA"
    assert m.is_region_total is False


def test_2019_victims_africa_region_total():
    entries = parse_country_breakdown_table(ROWS_2019_VICTIMS)
    region = _find(entries, "AFRICA")
    assert (region.male, region.female, region.unknown, region.total, region.pct) == (75, 474, 1, 550, 3.5)
    assert region.is_region_total is True


def test_2019_victims_blob_row_splits_all_three_countries():
    entries = parse_country_breakdown_table(ROWS_2019_VICTIMS)
    names = {e.name for e in entries if not e.is_region_total}
    assert names == {"MARRUECOS", "NIGERIA", "RESTO"}
    resto = _find(entries, "RESTO")
    assert (resto.male, resto.female, resto.unknown, resto.total) == (14, 90, 0, 104)


def test_2019_perpetrators_marruecos():
    entries = parse_country_breakdown_table(ROWS_2019_PERPS)
    m = _find(entries, "MARRUECOS")
    assert (m.male, m.female, m.unknown, m.total, m.pct) == (744, 7, 0, 751, 7.8)


def test_2022_perpetrators_marruecos_survives_columna_and_div0_noise():
    entries = parse_country_breakdown_table(ROWS_2022_PERPS)
    m = _find(entries, "MARRUECOS")
    assert (m.male, m.female, m.unknown, m.total, m.pct) == (889, 18, 0, 907, 7.8)


def test_2022_perpetrators_top_level_espanoles_row_not_emitted():
    entries = parse_country_breakdown_table(ROWS_2022_PERPS)
    assert "ESPANOLES" not in {e.name for e in entries}


def test_2024_victims_marruecos_reversed_columns():
    entries = parse_country_breakdown_table(ROWS_2024_VICTIMS, col_order_hint=HINT_2024_VICTIMS)
    m = _find(entries, "MARRUECOS")
    # source row is [Femenino=440, Masculino=87, No consta=0, Total=527] --
    # must land in the right named fields despite the reversed column order.
    assert (m.female, m.male, m.unknown, m.total, m.pct) == (440, 87, 0, 527, 2.31)
    assert m.region == "AFRICA"


def test_2024_victims_africa_region_total():
    entries = parse_country_breakdown_table(ROWS_2024_VICTIMS, col_order_hint=HINT_2024_VICTIMS)
    region = _find(entries, "AFRICA")
    assert (region.female, region.male, region.unknown, region.total, region.pct) == (596, 142, 0, 738, 3.24)


def test_2024_perpetrators_marruecos_no_sex_breakdown():
    entries = parse_country_breakdown_table(ROWS_2024_PERPS, col_order_hint=None)
    m = _find(entries, "MARRUECOS")
    assert m.male is None
    assert m.female is None
    assert m.unknown is None
    assert (m.total, m.pct) == (1100, 7.65)


def test_2024_perpetrators_africa_region_total_no_sex_breakdown():
    entries = parse_country_breakdown_table(ROWS_2024_PERPS, col_order_hint=None)
    region = _find(entries, "AFRICA")
    assert region.male is None
    assert (region.total, region.pct) == (1839, 12.79)
    assert region.is_region_total is True


def test_empty_rows_produce_no_entries():
    assert parse_country_breakdown_table([]) == []
    assert parse_country_breakdown_table([[None, None], ["", ""]]) == []
