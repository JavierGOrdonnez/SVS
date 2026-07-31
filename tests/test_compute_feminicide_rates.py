"""Tests for src/feminicides/compute_feminicide_rates.py (T24/T60/T92).

Covers estimate_nationality_population()'s sex-agnostic origin split, now
read directly from INE t.56936 (T89/B44/V46) rather than derived as
total-minus-foreign-stock (the real bug in B30 was upstream of this: was
back-derived from an assumed rate instead of real INE data; B44 then found
even the "real INE data" version was itself a derived subtraction across
mismatched sources). CI removed (B35).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.feminicides.compute_feminicide_rates import (
    estimate_nationality_population,
)


# ── estimate_nationality_population ─────────────────────────────

def test_estimate_nationality_population_reads_source_directly():
    pop_by_key = {
        (2024, 'female', 'spanish'): 800_000,
        (2024, 'female', 'foreign'): 200_000,
        (2024, 'female', 'total'): 1_000_000,
    }

    pop = estimate_nationality_population(2024, pop_by_key, 'female')

    assert pop['total'] == 1_000_000
    assert pop['otro_pais'] == 200_000
    assert pop['españa'] == 800_000  # source-reported, not total - foreign


def test_estimate_nationality_population_is_sex_agnostic():
    """The same function must serve both the female (victim) and male
    (perpetrator) population pipelines -- it should not special-case sex."""
    pop_by_key = {
        (2024, 'female', 'spanish'): 800_000,
        (2024, 'female', 'foreign'): 200_000,
        (2024, 'female', 'total'): 1_000_000,
        (2024, 'male', 'spanish'): 780_000,
        (2024, 'male', 'foreign'): 180_000,
        (2024, 'male', 'total'): 960_000,
    }

    female_pop = estimate_nationality_population(2024, pop_by_key, 'female')
    male_pop = estimate_nationality_population(2024, pop_by_key, 'male')

    assert female_pop['otro_pais'] == 200_000
    assert male_pop['otro_pais'] == 180_000
    assert female_pop['españa'] + female_pop['otro_pais'] == female_pop['total']
    assert male_pop['españa'] + male_pop['otro_pais'] == male_pop['total']


def test_estimate_nationality_population_falls_back_to_spanish_plus_foreign():
    """If a `total` row is somehow absent, total is spanish+foreign, not a
    silent KeyError -- but this never derives `españa` itself from total."""
    pop_by_key = {
        (2024, 'female', 'spanish'): 800_000,
        (2024, 'female', 'foreign'): 200_000,
    }

    pop = estimate_nationality_population(2024, pop_by_key, 'female')

    assert pop['total'] == 1_000_000
    assert pop['españa'] == 800_000
