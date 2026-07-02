"""Tests for MIR parser output schema invariants (V20, V21, V22).

V20: source_page/source_table/verified must live on MIRReport (report level),
     never on CategorySexBreakdown (category level) -- their value is
     structurally constant across every category in a given report.
V21: a multi-input parser run must emit exactly one MIRDataset JSON file,
     never one-per-input plus a redundant consolidated copy.
V22: a batch run must fail loud when two input PDFs infer to the same year,
     never silently merge both into one MIRDataset (found reviewing V21's
     fix, against the now-flattened data/sources/ dir where this collision
     is real, not hypothetical).
"""
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.mir_parser import (
    MIRRecord,
    MIRReport,
    CategorySexBreakdown,
    records_to_report,
    run_batch,
)


def make_records(year: int) -> list[MIRRecord]:
    return [
        MIRRecord(
            year=year, crime_category="total_sexual_crimes", legal_article="all",
            count=100, victims_spanish_pct=80.0, victims_foreign_pct=20.0,
            perp_spanish_pct=70.0, perp_foreign_pct=30.0,
            source_table="typology", source_page=7,
        ),
        MIRRecord(
            year=year, crime_category="violacion", legal_article="Art.179",
            count=60, victims_female=50, victims_male=10,
            perp_female=1, perp_male=59, notes="",
        ),
        MIRRecord(
            year=year, crime_category="agresion_sexual", legal_article="Art.178",
            count=40, victims_female=35, victims_male=5,
            perp_female=2, perp_male=38, notes="",
        ),
    ]


def test_v20_category_has_no_report_level_fields():
    fields = CategorySexBreakdown.model_fields
    assert "source_page" not in fields
    assert "source_table" not in fields
    assert "confidence" not in fields
    assert "verified" not in fields
    # notes legitimately varies per category (e.g. REFORM_NOTE) so it stays
    assert "notes" in fields


def test_v20_report_has_source_page_and_verified():
    fields = MIRReport.model_fields
    assert "source_page" in fields
    assert "source_table" in fields
    assert "verified" in fields
    assert "confidence" not in fields


def test_v20_verified_defaults_false():
    report = records_to_report(make_records(2024), 2024, "fake.pdf")
    assert report.verified is False
    assert report.source_page == 7


def test_v20_records_to_report_populates_categories_without_confidence():
    report = records_to_report(make_records(2024), 2024, "fake.pdf")
    assert len(report.categories) == 2
    for cat in report.categories:
        assert not hasattr(cat, "source_page")
        assert not hasattr(cat, "confidence")


def test_v21_run_batch_writes_exactly_one_file(tmp_path):
    def fake_parse_fn(pdf, year):
        return make_records(year)

    pairs = [(Path("2019.pdf"), 2019), (Path("2020.pdf"), 2020)]
    out = run_batch(pairs, fake_parse_fn, tmp_path)

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    assert files[0] == out
    assert out.name == "sexual_crimes_mir_2019-2020.json"


def test_v21_run_batch_single_year_names_file_by_that_year(tmp_path):
    def fake_parse_fn(pdf, year):
        return make_records(year)

    out = run_batch([(Path("2024.pdf"), 2024)], fake_parse_fn, tmp_path)
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    assert out.name == "sexual_crimes_mir_2024.json"


def test_v22_run_batch_rejects_duplicate_year_pdfs(tmp_path):
    def fake_parse_fn(pdf, year):
        return make_records(year)

    pairs = [
        (Path("MIR_Informe_DelitosSexuales2023.pdf"), 2023),
        (Path("MIR_GroupSexualViolence_2023.pdf"), 2023),
    ]
    with pytest.raises(ValueError, match="same year"):
        run_batch(pairs, fake_parse_fn, tmp_path)
    assert list(tmp_path.glob("*.json")) == []
