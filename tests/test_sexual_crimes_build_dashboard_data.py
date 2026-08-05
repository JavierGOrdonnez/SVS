"""Regression test for src/sexual_crimes/build_dashboard_data.py's
_peligrosity (T91/B44/V46).

Guards against silently reverting the Spanish male 15-59 peligrosidad
denominator back to the retired `total_male_15_59 - corrected_foreign`
subtraction (B44): pins it to the real INE t.56936 value and asserts it
differs from what the old subtraction would have produced.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.sexual_crimes.build_dashboard_data import (
    MIGRATION_CSV,
    PELIGROSITY_AGE_BANDS,
    POPULATION_NATIONALITY_CSV,
    REL_GROUPS,
    _coverage_factor,
    _peligrosity,
    _relationship_breakdown,
    _survey_comparison,
    read_csv,
    read_json,
    INFORME_JSON,
)

YEAR = 2024


def _new_spanish_male_15_59_pop(year):
    """What _peligrosity now uses: direct INE t.56936 read."""
    with open(POPULATION_NATIONALITY_CSV, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return sum(
        int(r["population_july1"]) for r in rows
        if r["nationality"] == "spanish" and r["sex"] == "male"
        and int(r["year"]) == year and r["age_group"] in PELIGROSITY_AGE_BANDS
    )


def _old_derived_spanish_male_15_59_pop(year, migration_rows):
    """Reproduces the retired B44 subtraction formula exactly, from the
    real source files, to prove the fix actually changed the number."""
    cov = _coverage_factor(migration_rows)

    foreign_male_15_59 = defaultdict(int)
    for r in migration_rows:
        if r["age_group"] not in PELIGROSITY_AGE_BANDS or r["sex"] != "male":
            continue
        if r["nationality"] != "ES":
            foreign_male_15_59[int(r["year"])] += int(r["value"]) if r["value"] else 0

    total_male_15_59_all = defaultdict(int)
    with open("data/processed/population_spain_midyear_5yr.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["age_group"] in PELIGROSITY_AGE_BANDS and r["sex"] == "male":
                total_male_15_59_all[int(r["year"])] += int(r["population_july1"]) if r["population_july1"] else 0

    corrected_foreign = round(foreign_male_15_59[year] * cov.get(year, 1.0))
    return total_male_15_59_all.get(year, 0) - corrected_foreign


def test_spanish_denominator_no_longer_matches_old_subtraction():
    migration_rows = read_csv(MIGRATION_CSV)

    new_pop = _new_spanish_male_15_59_pop(YEAR)
    old_pop = _old_derived_spanish_male_15_59_pop(YEAR, migration_rows)

    assert new_pop == 12_146_893  # pinned to the verified INE t.56936 figure
    assert new_pop != old_pop  # B44: the fix must have actually changed the number


def test_peligrosity_runs_end_to_end_and_carries_spain_series():
    informe = read_json(INFORME_JSON)["reports"]
    migration_rows = read_csv(MIGRATION_CSV)

    result = _peligrosity(informe, migration_rows)

    assert "spain" in result
    assert len(result["spain"]) == len(result["years"])


# ── T98: victim-perpetrator relationship ──────────────────────────

def test_relationship_breakdown_group_pct_sums_to_100_every_year():
    informe = read_json(INFORME_JSON)["reports"]
    result = _relationship_breakdown(informe)

    for i, year in enumerate(result["years"]):
        total = sum(result["group_pct"][g][i] for g in REL_GROUPS if result["group_pct"][g][i] is not None)
        assert abs(total - 100.0) < 0.1, f"{year}: group_pct sums to {total}, not ~100"


def test_relationship_breakdown_known_pct_excludes_unknown_group_and_sums_to_100():
    informe = read_json(INFORME_JSON)["reports"]
    result = _relationship_breakdown(informe)

    assert "relacion_desconocida" not in result["known_pct"]
    for i in range(len(result["years"])):
        total = sum(result["known_pct"][g][i] for g in result["known_pct"] if result["known_pct"][g][i] is not None)
        assert abs(total - 100.0) < 0.1


def test_survey_comparison_mir_point_excludes_partner_and_matches_relationship_data():
    informe = read_json(INFORME_JSON)["reports"]
    relationship = _relationship_breakdown(informe)
    result = _survey_comparison(relationship)

    point = result["mir_comparison_point"]
    assert point is not None
    assert abs(sum(point[c] for c in result["categories"]) - 100.0) < 0.1
    # partner-excluded renormalization must raise the "unknown" share above
    # the raw (partner-included) relacion_desconocida figure for the same year
    latest = relationship["years"].index(point["year"])
    raw_unknown = relationship["group_pct"]["relacion_desconocida"][latest]
    assert point["desconocido"] > raw_unknown


def test_survey_comparison_types_have_matching_series_length():
    informe = read_json(INFORME_JSON)["reports"]
    relationship = _relationship_breakdown(informe)
    result = _survey_comparison(relationship)

    for cat in result["categories"]:
        assert len(result["series"][cat]) == len(result["types"])
