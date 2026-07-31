"""Tests for the "Delitos de Odio" (hate crime) parser (OdioParser).

Covers:
  - classify_odio_category: label-normalization across the series' renames
    (DISCAPACIDAD -> DIVERSIDAD FUNCIONAL -> PERSONA CON DISCAPACIDAD ->
    DELITOS DE ODIO CONTRA PERSONAS CON DISCAPACIDAD -> DISFOBIA, 2021+ SES
    portal label) and additions (ANTIGITANISMO 2019+, DISCRIMINACION
    GENERACIONAL/ENFERMEDAD 2018+, ISLAMOFOBIA 2024+ as its own category,
    not folded into DISFOBIA/discapacidad), plus the 3-tier total structure
    (TOTAL DELITOS / INFRAC. ADM. / TOTAL DELITOS E INCIDENTES) introduced
    in 2019.
  - OdioParser._cluster_rows: the y-tolerance row reconstruction that
    re-joins a label+numbers row split across two word-clusters ~1-2pt
    apart, without merging distinct ámbito rows (always >=10pt apart).
  - OdioParser end-to-end against the real 2016 and 2023 source PDFs
    (skipped if the PDFs aren't present), cross-checked against
    hand-verified totals from data/sources/MIR_InformeDelitosOdio_*.pdf.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.mir_parser import (
    classify_odio_category,
    OdioParser,
    run_odio,
    run_odio_batch,
)

SOURCES_DIR = Path(__file__).resolve().parent.parent / "data" / "sources"


# ── classify_odio_category ──

@pytest.mark.parametrize("label,expected", [
    ("DISCAPACIDAD", "discapacidad"),
    ("DIVERSIDAD FUNCIONAL", "discapacidad"),
    ("PERSONA CON DISCAPACIDAD", "discapacidad"),
    ("DELITOS DE ODIO CONTRA PERSONAS CON DISCAPACIDAD", "discapacidad"),
    ("DISFOBIA", "discapacidad"),
    ("ISLAMOFOBIA", "islamofobia"),
    ("ANTIGITANISMO", "antigitanismo"),
    ("ANTISEMITISMO", "antisemitismo"),
    ("APOROFOBIA", "aporofobia"),
    ("CREENCIAS O PRACTICAS RELIGIOSAS", "creencias_practicas_religiosas"),
    ("ORIENTACION O IDENTIDAD SEXUAL", "orientacion_identidad_sexual_genero"),
    ("ORIENTAC. SEXUAL E IDENT. GENERO", "orientacion_identidad_sexual_genero"),
    ("RACISMO/XENOFOBIA", "racismo_xenofobia"),
    ("IDEOLOGIA", "ideologia"),
    ("DISCRIMINACION POR SEXO/GENERO", "discriminacion_sexo_genero"),
    ("DISCRIMINACION POR RAZON DE SEXO/GENERO", "discriminacion_sexo_genero"),
    ("DISCRIMINACION GENERACIONAL", "discriminacion_generacional"),
    ("DISCRIMINACION GENERAC. (AGEISM)", "discriminacion_generacional"),
    ("DISCRIMINACION POR RAZON DE ENFERMEDAD", "discriminacion_enfermedad"),
    ("INFRAC. ADM. Y RESTO INCIDENTES", "infracciones_administrativas"),
    ("INFRAC. ADM. Y RESTO DE INCIDENTES", "infracciones_administrativas"),
    ("TOTAL", "total_delitos"),
    (". TOTAL", "total_delitos"),
    ("TOTAL DELITOS", "total_delitos"),
    ("TOTAL DELITOS E INCIDENTES DE ODIO", "total_con_incidentes"),
])
def test_classify_odio_category(label, expected):
    assert classify_odio_category(label) == expected


def test_classify_odio_category_unrecognized_returns_none():
    assert classify_odio_category("HECHOS CONOCIDOS 2018 2019 %Variacion") is None
    assert classify_odio_category("DISTRIBUCION PORCENTUAL DE LOS HECHOS") is None


def test_orientacion_not_confused_with_discriminacion_sexo_genero():
    # ORIENTACION SEXUAL E IDENTIDAD DE GENERO contains "SEXUAL" and
    # "GENERO" but must NOT be classified as discriminacion_sexo_genero
    # (which requires "DISCRIMINACION" too, absent from this label).
    assert classify_odio_category("ORIENTACION SEXUAL E IDENTIDAD DE GENERO") == "orientacion_identidad_sexual_genero"


# ── row clustering ──

def _w(text, top, x0):
    return {"text": text, "top": top, "x0": x0}


def test_cluster_rows_merges_split_label_and_numbers():
    # Same logical row split 1pt apart (numbers-cluster, then label-cluster)
    # -- observed in 2023's TOTAL DELITOS row.
    words = [
        _w("1724", 262.0, 354.1), _w("1796", 262.0, 387.4), _w("2150", 262.0, 415.8),
        _w("TOTAL", 263.0, 115.2), _w("DELITOS", 263.0, 138.6),
    ]
    rows = OdioParser._cluster_rows(words)
    assert len(rows) == 1
    texts = [w["text"] for w in rows[0]]
    assert texts == ["TOTAL", "DELITOS", "1724", "1796", "2150"]  # sorted by x0


def test_cluster_rows_keeps_distinct_ambitos_separate():
    # ~10pt gap between categories must NOT merge.
    words = [
        _w("ANTIGITANISMO", 139.0, 115.2), _w("18", 140.0, 362.1),
        _w("ANTISEMITISMO", 150.0, 115.2), _w("11", 151.0, 362.1),
    ]
    rows = OdioParser._cluster_rows(words)
    assert len(rows) == 2
    assert rows[0][0]["text"] == "ANTIGITANISMO"
    assert rows[1][0]["text"] == "ANTISEMITISMO"


def test_int_token_re_accepts_both_thousands_formats():
    # 2019's own TOTAL DELITOS row renders "1476" (no separator) and
    # "1.598" (dot-separator) in the same table.
    assert OdioParser.INT_TOKEN_RE.match("1476")
    assert OdioParser.INT_TOKEN_RE.match("1.598")
    assert OdioParser.INT_TOKEN_RE.match("9")
    assert not OdioParser.INT_TOKEN_RE.match("8,7%")
    assert not OdioParser.INT_TOKEN_RE.match("100,0%")


# ── end-to-end against real PDFs ──

def _pdf(name):
    p = SOURCES_DIR / name
    if not p.exists():
        pytest.skip(f"{name} not present in data/sources/")
    return p


def test_2016_end_to_end_matches_hand_verified_totals():
    records = run_odio(_pdf("MIR_InformeDelitosOdio_2016.pdf"), 2016)
    by_cat = {r.crime_category: r.count for r in records}
    assert by_cat["total_hate_crimes"] == 1272
    assert by_cat["total_delitos"] == 1272  # 2016 has no infrac-adm split yet
    assert by_cat["discapacidad"] == 262
    assert by_cat["racismo_xenofobia"] == 416
    assert sum(v for k, v in by_cat.items() if k not in ("total_hate_crimes", "total_delitos")) == 1272


def test_2023_end_to_end_matches_hand_verified_totals_and_3tier_structure():
    records = run_odio(_pdf("MIR_InformeDelitosOdio_2023.pdf"), 2023)
    by_cat = {r.crime_category: r.count for r in records}
    assert by_cat["total_hate_crimes"] == 2268
    assert by_cat["total_delitos"] == 2150
    assert by_cat["infracciones_administrativas"] == 118
    assert by_cat["total_delitos"] + by_cat["infracciones_administrativas"] == by_cat["total_hate_crimes"]
    ambitos = [k for k in by_cat if k not in ("total_hate_crimes", "total_delitos", "infracciones_administrativas")]
    assert sum(by_cat[k] for k in ambitos) == by_cat["total_delitos"]


def test_no_validation_warnings_emitted_for_any_year(capsys):
    for name, year in [
        ("MIR_InformeDelitosOdio_2016.pdf", 2016),
        ("MIR_InformeDelitosOdio_2019.pdf", 2019),
        ("MIR_InformeDelitosOdio_2021.pdf", 2021),
        ("MIR_InformeDelitosOdio_2023.pdf", 2023),
    ]:
        run_odio(_pdf(name), year)
    captured = capsys.readouterr()
    assert "VALIDATION" not in captured.err


def test_run_odio_batch_skips_2022_gap_and_names_file_with_visible_gap(tmp_path):
    import re
    pdfs = sorted(SOURCES_DIR.glob("MIR_InformeDelitosOdio_*.pdf"))
    if len(pdfs) < 2:
        pytest.skip("not enough MIR_InformeDelitosOdio_*.pdf present")
    out = run_odio_batch(pdfs, tmp_path)
    assert out.exists()
    assert not re.search(r"(?<!\d)2022(?!\d)", out.stem)  # 2022 has no dedicated PDF
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
