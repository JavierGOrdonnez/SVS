"""Tests for src/parsers/mir_migrant_nationality_parser.py's
load_general_crime_anuario_rows() (T27).

Covers: (a) foreign/spanish row pairing per year x category, (b) spanish
count/pct correctly derived as total minus foreign (not source-reported),
(c) years present in only one of the two metrics are skipped rather than
producing a partial/garbage row.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.parsers.mir_migrant_nationality_parser import load_general_crime_anuario_rows


def _write_fixture(path: Path, rows):
    fieldnames = ["year", "category", "metric", "sex", "count", "source_edition", "source_page", "notes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def test_foreign_spanish_pairing_and_derived_spanish_count(tmp_path):
    fixture = tmp_path / "mir_anuario_general_crime.csv"
    _write_fixture(fixture, [
        {"year": 2023, "category": "homicide", "metric": "detenciones_foreign", "sex": "all",
         "count": 568, "source_edition": 2023, "source_page": 121, "notes": ""},
        {"year": 2023, "category": "homicide", "metric": "detenciones_total", "sex": "all",
         "count": 1631, "source_edition": 2023, "source_page": 106, "notes": ""},
        # sex-split rows must be ignored (only sex=="all" feeds the headline numerator)
        {"year": 2023, "category": "homicide", "metric": "detenciones_foreign", "sex": "male",
         "count": 533, "source_edition": 2023, "source_page": 121, "notes": ""},
    ])

    rows = load_general_crime_anuario_rows(fixture)

    assert len(rows) == 2
    by_nat = {r["nationality_group"]: r for r in rows}
    assert by_nat["foreign"]["count"] == 568
    assert by_nat["spanish"]["count"] == 1631 - 568
    assert by_nat["foreign"]["pct"] == 34.8
    assert by_nat["spanish"]["pct"] == 65.2
    for r in rows:
        assert r["crime_type"] == "general_crime_homicide"
        assert r["actor_role"] == "perpetrator"
        assert r["denominator_value"] == 1631


def test_year_missing_one_metric_is_skipped(tmp_path):
    fixture = tmp_path / "mir_anuario_general_crime.csv"
    _write_fixture(fixture, [
        {"year": 2012, "category": "homicide", "metric": "detenciones_total", "sex": "all",
         "count": 1325, "source_edition": 2016, "source_page": 171, "notes": ""},
        {"year": 2012, "category": "homicide", "metric": "hechos_conocidos_total", "sex": "all",
         "count": 1125, "source_edition": 2016, "source_page": 167, "notes": ""},
    ])

    rows = load_general_crime_anuario_rows(fixture)

    assert rows == []


def test_missing_source_file_returns_empty(tmp_path):
    assert load_general_crime_anuario_rows(tmp_path / "does_not_exist.csv") == []
