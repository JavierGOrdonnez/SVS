"""Tests for the SES hate-crime nationality megatabla parser
(src/crime/parse_ses_odio_nationality.py).

Covers:
  - parse_raw: column-count-based layout detection (06019 detentions has a
    leading Calificacion column that 06013 victimizations doesn't), national
    filtering, Spanish thousands-separator parsing.
  - validate: nationality sub-totals reconciling against 'TOTAL nacionalidad'.
  - summarize_spanish_share: per (year, ambito) Espana/foreign/pct, using the
    correct total-sexo label per table (Ambos sexos vs. TOTAL sexo).
  - Regression check against the real cached SES output (skipped if the raw
    CSVs haven't been fetched into data/raw/ yet), matching the hand-verified
    figures recorded in data/sources/mir_delitos_odio.md: 2023 detainees,
    all ambitos, national: 1,161 total / 914 Espana = 78.7% Spanish; 2023
    detainees, Orientacion sexual e identidad de genero ambito: 194/269 =
    72.1% Spanish.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.crime.parse_ses_odio_nationality import (
    parse_raw,
    validate,
    summarize_spanish_share,
    TOTAL_SEXO_LABEL,
    NATIONAL_ROW,
)

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

# ── 06019-shape fixture (Calificacion, CCAA, Nacionalidad, Periodo, Ambito, Sexo, Total) ──
DETENIDOS_CSV = (
    "﻿Calificación;Comunidades autónomas;Nacionalidad;Período;Ámbito;Sexo;Total\n"
    "INFRACC. PENALES;TOTAL NACIONAL;ESPAÑA;2023;RACISMO/XENOFOBIA;Masculino;300\n"
    "INFRACC. PENALES;TOTAL NACIONAL;ESPAÑA;2023;RACISMO/XENOFOBIA;Femenino;100\n"
    "INFRACC. PENALES;TOTAL NACIONAL;ESPAÑA;2023;RACISMO/XENOFOBIA;Ambos sexos;400\n"
    "INFRACC. PENALES;TOTAL NACIONAL;MARRUECOS;2023;RACISMO/XENOFOBIA;Ambos sexos;100\n"
    "INFRACC. PENALES;TOTAL NACIONAL;TOTAL nacionalidad;2023;RACISMO/XENOFOBIA;Ambos sexos;1.500\n"
    "INFRACC. PENALES;ANDALUCÍA;ESPAÑA;2023;RACISMO/XENOFOBIA;Ambos sexos;50\n"
)

# ── 06013-shape fixture (no Calificacion column, different sex labels) ──
VICTIMAS_CSV = (
    "﻿Comunidades autónomas;Nacionalidad;Periodos:;Ámbito;Sexo;Total\n"
    "TOTAL NACIONAL;ESPAÑA;2023;IDEOLOGÍA;Masculino;40\n"
    "TOTAL NACIONAL;ESPAÑA;2023;IDEOLOGÍA;TOTAL sexo;60\n"
    "TOTAL NACIONAL;COLOMBIA;2023;IDEOLOGÍA;TOTAL sexo;20\n"
    "TOTAL NACIONAL;TOTAL nacionalidad;2023;IDEOLOGÍA;TOTAL sexo;80\n"
    "TOTAL NACIONAL;ESPAÑA;2023;IDEOLOGÍA;Persona jurídica;0\n"
)


def test_parse_raw_detects_7_column_layout_and_filters_national():
    df = parse_raw(DETENIDOS_CSV)
    assert "calificacion" not in df.columns
    assert "ccaa" not in df.columns
    # the ANDALUCÍA row must be dropped
    assert set(df["nacionalidad"].unique()) == {"ESPAÑA", "MARRUECOS", "TOTAL nacionalidad"}
    espana_total = df[(df["nacionalidad"] == "ESPAÑA") & (df["sexo"] == "Ambos sexos")]["total"].iloc[0]
    assert espana_total == 400


def test_parse_raw_detects_6_column_layout():
    df = parse_raw(VICTIMAS_CSV)
    assert list(df.columns) == ["nacionalidad", "anyo", "ambito", "sexo", "total"]
    assert len(df) == 5  # ANDALUCÍA-equivalent already absent from fixture


def test_parse_raw_parses_spanish_thousands_separator():
    df = parse_raw(DETENIDOS_CSV)
    total_row = df[(df["nacionalidad"] == "TOTAL nacionalidad") & (df["sexo"] == "Ambos sexos")]
    assert total_row["total"].iloc[0] == 1500


def test_validate_flags_reconciliation_mismatch():
    df = parse_raw(DETENIDOS_CSV)
    # 400 (España) + 100 (Marruecos) = 500 != 1500 (TOTAL nacionalidad) -> real
    # tables always reconcile; this fixture deliberately doesn't, to prove
    # validate() catches it.
    errors = validate(df, TOTAL_SEXO_LABEL["06019"])
    assert len(errors) == 1
    assert "2023" in errors[0] and "RACISMO" in errors[0]


def test_validate_passes_on_reconciling_victims_fixture():
    df = parse_raw(VICTIMAS_CSV)
    # 60 (España) + 20 (Colombia) = 80 == TOTAL nacionalidad
    errors = validate(df, TOTAL_SEXO_LABEL["06013"])
    assert errors == []


def test_summarize_spanish_share_detenidos():
    df = parse_raw(DETENIDOS_CSV)
    summary = summarize_spanish_share(df, TOTAL_SEXO_LABEL["06019"])
    row = summary[summary["ambito"] == "RACISMO/XENOFOBIA"].iloc[0]
    assert row["espana"] == 400
    assert row["total_nacionalidad"] == 1500
    assert row["foreign"] == 1100
    assert row["pct_spanish"] == pytest.approx(26.7, abs=0.1)


def test_summarize_spanish_share_victimas_uses_total_sexo_label():
    df = parse_raw(VICTIMAS_CSV)
    summary = summarize_spanish_share(df, TOTAL_SEXO_LABEL["06013"])
    row = summary[summary["ambito"] == "IDEOLOGÍA"].iloc[0]
    # must read the 'TOTAL sexo' row (60), not sum Masculino+TOTAL sexo+Persona juridica
    assert row["espana"] == 60
    assert row["total_nacionalidad"] == 80
    assert row["pct_spanish"] == pytest.approx(75.0)


# ── Regression against real cached SES output (skipped if not fetched yet) ──

DETENIDOS_SUMMARY = RAW_DIR / "hate_crimes_ses_nacionalidad_detenidos_summary_2021-2024.csv"


@pytest.mark.skipif(not DETENIDOS_SUMMARY.exists(), reason="SES data not fetched into data/raw/ yet")
def test_2023_detainee_totals_match_hand_verified_figures():
    summary = pd.read_csv(DETENIDOS_SUMMARY)
    total_row = summary[(summary["anyo"] == 2023) & (summary["ambito"] == "TOTAL ámbito")].iloc[0]
    assert total_row["total_nacionalidad"] == 1161
    assert total_row["espana"] == 914
    assert total_row["pct_spanish"] == pytest.approx(78.7, abs=0.1)

    osig_row = summary[
        (summary["anyo"] == 2023) & (summary["ambito"] == "ORIENTACIÓN SEXUAL E IDENTIDAD DE GÉNERO")
    ].iloc[0]
    assert osig_row["total_nacionalidad"] == 269
    assert osig_row["espana"] == 194
    assert osig_row["pct_spanish"] == pytest.approx(72.1, abs=0.1)
