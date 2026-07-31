"""Tests for src/analysis/parse_ine_population_nationality.py (T89/B44).

Covers: age-band collapse into the shared 17-band pyramid scale (esp. the
80-84/85-89/90+ -> 80+ merge), the "Todas las edades" -> age_group="all"
passthrough, nationality filtering (individual countries dropped), the
2002 floor (V46: no pre-2002 backfill), and July-1-only filtering.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analysis.parse_ine_population_nationality import (
    AGE_MAP,
    MIN_YEAR,
    NATIONALITY_MAP,
    parse_periodo,
    parse_value,
    main,
)


# ── pure helpers ─────────────────────────────────────────────

def test_parse_value_handles_spanish_thousands_dots():
    assert parse_value('"42.169.185"') == 42169185
    assert parse_value("1885497") == 1885497


def test_parse_value_missing():
    assert parse_value('""') is None
    assert parse_value("..") is None


def test_parse_periodo_july_first():
    assert parse_periodo("1 de julio de 2024") == (2024, "07-01")


def test_parse_periodo_unknown_month_rejected():
    assert parse_periodo("garbage") is None


def test_age_map_collapses_80_plus():
    assert AGE_MAP["De 80 a 84 años"] == "80+"
    assert AGE_MAP["De 85 a 89 años"] == "80+"
    assert AGE_MAP["90 y más años"] == "80+"


def test_age_map_all_ages_passthrough():
    assert AGE_MAP["Todas las edades"] == "all"


def test_nationality_map_only_three_values():
    assert NATIONALITY_MAP == {"Española": "spanish", "Extranjera": "foreign", "Total": "total"}


def test_min_year_floor_is_2002():
    assert MIN_YEAR == 2002


# ── end-to-end (T89) ─────────────────────────────────────────

RAW_CSV = (
    "Nacionalidad;Grupo quinquenal de edad;Sexo;Periodo;Total\n"
    'Española;Todas las edades;Total;1 de julio de 2024;42.169.185\n'
    'Española;Todas las edades;Total;1 de abril de 2024;""\n'  # non-July -- dropped
    'Española;Todas las edades;Total;1 de julio de 2001;39.000.000\n'  # pre-2002 -- dropped
    'Española;De 80 a 84 años;Hombres;1 de julio de 2024;560.737\n'
    'Española;De 85 a 89 años;Hombres;1 de julio de 2024;327.384\n'
    'Española;90 y más años;Hombres;1 de julio de 2024;193.888\n'
    'Marruecos;Todas las edades;Total;1 de julio de 2024;900.000\n'  # individual country -- dropped
    'Extranjera;Todas las edades;Total;1 de julio de 2024;7.000.000\n'
)


def test_main_end_to_end(tmp_path):
    in_path = tmp_path / "56936.csv"
    in_path.write_text(RAW_CSV, encoding="utf-8")
    out_path = tmp_path / "out.csv"

    main(str(in_path), str(out_path))

    rows = {}
    with open(out_path, encoding="utf-8") as f:
        import csv
        for r in csv.DictReader(f):
            rows[(int(r["year"]), r["sex"], r["age_group"], r["nationality"])] = int(r["population_july1"])

    # July-1 all-age Spanish total kept; April and pre-2002 rows dropped
    assert rows[(2024, "all", "all", "spanish")] == 42169185
    assert (2024, "all", "all", "spanish") in rows
    assert not any(year == 2001 for (year, *_rest) in rows)

    # 80-84 + 85-89 + 90+ summed into one 80+ bucket
    assert rows[(2024, "male", "80+", "spanish")] == 560737 + 327384 + 193888

    # individual-country row (Marruecos) never makes it into the output
    assert not any(k[3] == "Marruecos" for k in rows)

    # foreign/total nationality tags pass through untouched
    assert rows[(2024, "all", "all", "foreign")] == 7000000
