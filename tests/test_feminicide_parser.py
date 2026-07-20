"""Tests for the Delegación del Gobierno feminicide PDF parser (T19/T20).

Covers the generic table-extraction helpers (_numbers_after, _slice_block,
_extract_simple_table, _extract_victim_perp_table, _extract_flat_table,
_extract_relationship_table), the legacy/modern format dispatch in
parse_pdf(), and run_batch()'s V21 (exactly one output file, named by year
range) / V22 (raise on duplicate-year collision) invariants -- mirroring
test_mir_parser_schema.py's coverage of the same invariants for mir_parser.py.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers import feminicide_parser as fp
from src.parsers.feminicide_parser import (
    _extract_flat_table,
    _extract_relationship_table,
    _extract_simple_table,
    _extract_victim_perp_table,
    _numbers_after,
    _slice_block,
    infer_year,
)


# ── _numbers_after ──────────────────────────────────────────────

def test_numbers_after_returns_tokens_following_label():
    text = "Número 10 20 30 % 1.0 2.0"
    assert _numbers_after(r"Número", text) == ["10", "20", "30", "1.0", "2.0"]


def test_numbers_after_respects_limit():
    text = "Número 10 20 30"
    assert _numbers_after(r"Número", text, limit=2) == ["10", "20"]


def test_numbers_after_returns_empty_when_label_missing():
    assert _numbers_after(r"Número", "no label here") == []


# ── _slice_block ────────────────────────────────────────────────

def test_slice_block_extracts_between_two_patterns():
    text = "PREFIX Comunidad/ciudad autónoma DATA HERE Grupo de edad SUFFIX"
    result = _slice_block(text, r"Comunidad/ciudad autónoma", r"Grupo de edad")
    assert result == " DATA HERE "


def test_slice_block_returns_none_when_start_pattern_missing():
    assert _slice_block("no match here", r"Comunidad/ciudad autónoma", r"Grupo de edad") is None


def test_slice_block_reads_to_end_when_end_pattern_missing():
    result = _slice_block("START DATA HERE", r"START", None)
    assert result == " DATA HERE"


# ── _extract_simple_table (e.g. Table 2.1 regional) ─────────────

def test_extract_simple_table_drops_leading_total_row():
    vocab = ["Andalucía", "Aragón", "Cataluña"]
    # Número: TOTAL=69, Andalucía=17, Aragón=3, Cataluña=8
    # %:      TOTAL=100.0, Andalucía=24.6, Aragón=4.3, Cataluña=11.6
    block = "Número 69 17 3 8 % 100.0 24.6 4.3 11.6 Grupo de edad"
    result = _extract_simple_table(block, vocab)
    assert [(c.label, c.count, c.pct) for c in result] == [
        ("Andalucía", 17, 24.6), ("Aragón", 3, 4.3), ("Cataluña", 8, 11.6),
    ]


def test_extract_simple_table_returns_empty_when_not_enough_numbers():
    vocab = ["Andalucía", "Aragón", "Cataluña"]
    block = "Número 69 17 % 100.0"
    assert _extract_simple_table(block, vocab) == []


# ── _extract_victim_perp_table (e.g. Table 2.3 origin) ──────────

def test_extract_victim_perp_table_splits_victims_and_perpetrators():
    vocab = ["España", "Otro país"]
    block = (
        "Mujeres víctimas mortales Número 49 33 16 % 100.0 67.3 32.7 "
        "Presuntos agresores Número 49 31 18 % 100.0 63.3 36.7"
    )
    result = _extract_victim_perp_table(block, vocab)
    assert [
        (c.label, c.victim_count, c.victim_pct, c.perp_count, c.perp_pct)
        for c in result
    ] == [
        ("España", 33, 67.3, 31, 63.3),
        ("Otro país", 16, 32.7, 18, 36.7),
    ]


def test_extract_victim_perp_table_handles_missing_perp_block():
    vocab = ["España", "Otro país"]
    block = "Mujeres víctimas mortales Número 49 33 16 % 100.0 67.3 32.7"
    result = _extract_victim_perp_table(block, vocab)
    assert result[0].victim_count == 33
    assert result[0].perp_count is None
    assert result[0].perp_pct is None


# ── _extract_flat_table (Tables 3.1-3.4, TOTAL rows kept) ───────

def test_extract_flat_table_keeps_all_labels_1to1():
    labels = ["TOTAL", "Con denuncia", "Sin denuncia"]
    block = "Número 100 60 40 % 100.0 60.0 40.0"
    result = _extract_flat_table(block, labels)
    assert [(c.label, c.count, c.pct) for c in result] == [
        ("TOTAL", 100, 100.0), ("Con denuncia", 60, 60.0), ("Sin denuncia", 40, 40.0),
    ]


# ── _extract_relationship_table (Table 2.4) ─────────────────────

def test_extract_relationship_table_splits_relationship_and_cohabitation():
    from src.parsers.feminicide_parser import COHABITATION, RELATIONSHIP_TYPES

    block = "Número 49 30 19 49 25 20 4 % 100.0 61.2 38.8 100.0 51.0 40.8 8.2"
    relationship, cohabitation = _extract_relationship_table(block)

    assert [(c.label, c.count, c.pct) for c in relationship] == [
        (RELATIONSHIP_TYPES[0], 30, 61.2), (RELATIONSHIP_TYPES[1], 19, 38.8),
    ]
    assert [(c.label, c.count, c.pct) for c in cohabitation] == [
        (COHABITATION[0], 25, 51.0), (COHABITATION[1], 20, 40.8), (COHABITATION[2], 4, 8.2),
    ]


# ── infer_year ───────────────────────────────────────────────────

def test_infer_year_extracts_four_digit_year():
    assert infer_year(Path("VMujeres_2024.pdf")) == 2024


def test_infer_year_returns_none_when_no_year():
    assert infer_year(Path("VMujeres_final.pdf")) is None


# ── parse_pdf format dispatch (2003-2005 legacy vs 2006+ modern) ─

def test_parse_pdf_dispatches_to_modern_format_when_tabla_2_1_present(monkeypatch):
    monkeypatch.setattr(fp, "extract_text", lambda path, timeout=30: "some text with Tabla 2.1 in it")
    report = fp.parse_pdf(Path("VMujeres_2024.pdf"))
    assert report.confidence == "high"
    assert report.notes == ""


def test_parse_pdf_dispatches_to_legacy_format_when_tabla_2_1_absent(monkeypatch):
    monkeypatch.setattr(fp, "extract_text", lambda path, timeout=30: "old ficha resumen text, no numbered tables")
    report = fp.parse_pdf(Path("VMujeres_2004.pdf"))
    assert report.confidence == "low"
    assert "Legacy" in report.notes
    assert report.regional == []


# ── run_batch: V21 (exactly one output file) / V22 (year collision) ─

def _fake_parse_pdf(pdf_path, year=None):
    return fp.FeminicideReport(year=year, source_document=pdf_path.name)


def test_run_batch_writes_one_file_named_by_year_range(tmp_path, monkeypatch):
    monkeypatch.setattr(fp, "parse_pdf", _fake_parse_pdf)

    pdfs = [Path("VMujeres_2019.pdf"), Path("VMujeres_2020.pdf")]
    out = fp.run_batch(pdfs, tmp_path)

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    assert files[0] == out
    assert out.name == "feminicidios_delegacion_2019-2020.json"


def test_run_batch_single_year_names_file_by_that_year(tmp_path, monkeypatch):
    monkeypatch.setattr(fp, "parse_pdf", _fake_parse_pdf)

    out = fp.run_batch([Path("VMujeres_2024.pdf")], tmp_path)
    assert out.name == "feminicidios_delegacion_2024.json"


def test_run_batch_rejects_duplicate_year_pdfs(tmp_path, monkeypatch):
    monkeypatch.setattr(fp, "parse_pdf", _fake_parse_pdf)

    pdfs = [Path("VMujeres_2023.pdf"), Path("VMujeres_2023_v2.pdf")]
    with pytest.raises(ValueError, match="same year"):
        fp.run_batch(pdfs, tmp_path)
    assert list(tmp_path.glob("*.json")) == []
