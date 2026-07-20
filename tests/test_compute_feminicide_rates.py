"""Tests for src/feminicides/compute_feminicide_rates.py (T24/T60).

Covers estimate_nationality_population()'s sex-agnostic origin split (the
real bug in B30 was here: population was back-derived from an assumed rate
instead of real INE data). CI removed (B35).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.feminicides.compute_feminicide_rates import (
    estimate_nationality_population,
)


# ── estimate_nationality_population ─────────────────────────────

def test_estimate_nationality_population_splits_total_by_foreign_stock():
    total_by_year = {2024: 1_000_000}
    foreign_by_sex = {2024: {'female': 200_000, 'male': 180_000, 'all': 380_000}}

    pop = estimate_nationality_population(2024, total_by_year, foreign_by_sex, 'female')

    assert pop['total'] == 1_000_000
    assert pop['otro_pais'] == 200_000
    assert pop['españa'] == 800_000  # total - foreign, not total + foreign


def test_estimate_nationality_population_is_sex_agnostic():
    """The same function must serve both the female (victim) and male
    (perpetrator) population pipelines -- it should not special-case sex."""
    total_by_year = {2024: 1_000_000}
    foreign_by_sex = {2024: {'female': 200_000, 'male': 180_000, 'all': 380_000}}

    female_pop = estimate_nationality_population(2024, total_by_year, foreign_by_sex, 'female')
    male_pop = estimate_nationality_population(2024, total_by_year, foreign_by_sex, 'male')

    assert female_pop['otro_pais'] == 200_000
    assert male_pop['otro_pais'] == 180_000
    assert female_pop['españa'] + female_pop['otro_pais'] == female_pop['total']
    assert male_pop['españa'] + male_pop['otro_pais'] == male_pop['total']
