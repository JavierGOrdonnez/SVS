"""Tests for src/crime/analyze_cohort_crime_rate.py's Test B decomposition
(T41), covering the B43 backprop fixes (see SPEC.md B43, V45):

  1. A hidden/undocumented population added via the regularization
     sensitivity extension (`extra_stock`) must land entirely in
     cohort_pop, not settled_pop -- B42 originally added it to settled_pop
     (assuming long tenure); B43 revised this to cohort_pop (recent
     arrivals is the more defensible read of why an extraordinary, lower-
     bar amnesty was needed at all).
  2. The settled sub-population's expected rate must be scaled by an
     independently-measured reference-population trend (Test E's Spanish
     rate) rather than frozen at the historical baseline -- freezing it
     silently attributed the whole of any shared, non-group-specific
     societal rate rise to the tiny cohort bucket, inflating the apparent
     cohort/settled ratio (this is what made B42's fix alone produce
     implausible 4x-6x ratios).
  3. A negative implied cohort rate (the trend-adjusted settled expectation
     alone exceeds the observed total) is reported as `undefined`, not
     dressed up as a valid "significantly below baseline" rate comparison.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.crime import analyze_cohort_crime_rate as m


def _flat_spanish_data(years, spanish_male_count=500.0):
    return {y: {"spanish_male_count": spanish_male_count, "total_perp": 0, "foreign_total": 0}
            for y in years}


# ── cohort_pop_for_year: net-stock-delta (B42) ──────────────────────────

def test_cohort_pop_for_year_is_net_stock_delta():
    stock_by_year = {2019: 1000, 2022: 1200}
    assert m.cohort_pop_for_year(stock_by_year, 2022) == 200
    assert m.cohort_pop_for_year(stock_by_year, 2022, window=3) == 200


# ── regularization extra_stock lands in cohort, not settled (B43) ───────

def test_regularization_extra_lands_in_cohort_not_settled(monkeypatch):
    monkeypatch.setattr(m, "TEST_YEARS", [2022, 2023])
    stock_by_year = {2016: 900, 2019: 1000, 2020: 1000, 2021: 1000, 2022: 1200, 2023: 1300}
    crime_by_year = {2019: (100, "high"), 2022: (150, "high"), 2023: (170, "high")}
    years = (2019, 2022, 2023)
    spanish_data = _flat_spanish_data(years)
    spanish_male_pop = {y: 100000.0 for y in years}

    unadjusted = m.run_test_b("TESTGRP", "TG", stock_by_year, crime_by_year, [2019],
                               "baseline_label", spanish_data, spanish_male_pop, extra_stock=0)
    adjusted = m.run_test_b("TESTGRP", "TG", stock_by_year, crime_by_year, [2019],
                             "baseline_label", spanish_data, spanish_male_pop, extra_stock=50)

    by_year_unadj = {r["year"]: r for r in unadjusted}
    by_year_adj = {r["year"]: r for r in adjusted}
    assert set(by_year_unadj) == set(by_year_adj) == {2019, 2022, 2023}
    for year in by_year_unadj:
        # settled_pop is untouched by the hidden population...
        assert (by_year_adj[year]["settled_pop_male_15_59"]
                == by_year_unadj[year]["settled_pop_male_15_59"])
        # ...cohort_pop absorbs all of it, every year (baseline included).
        assert (by_year_adj[year]["cohort_pop_male_15_59"]
                == by_year_unadj[year]["cohort_pop_male_15_59"] + 50)


# ── settled expectation scales with the Spanish reference trend (B43) ──

def test_trend_adjustment_shrinks_ratio_vs_frozen_baseline(monkeypatch):
    monkeypatch.setattr(m, "TEST_YEARS", [2022])
    stock_by_year = {2016: 900, 2019: 1000, 2022: 1200}
    crime_by_year = {2019: (100, "high"), 2022: (200, "high")}
    spanish_data = {
        2019: {"spanish_male_count": 500.0, "total_perp": 0, "foreign_total": 0},
        2022: {"spanish_male_count": 600.0, "total_perp": 0, "foreign_total": 0},
    }
    spanish_male_pop = {2019: 100000.0, 2022: 100000.0}
    # spanish_rate 2019=0.005, 2022=0.006 -> trend = 1.2

    rows = m.run_test_b("TESTGRP", "TG", stock_by_year, crime_by_year, [2019],
                         "baseline_label", spanish_data, spanish_male_pop)
    test_row = next(r for r in rows if r["role"] == "test")

    assert test_row["r_settled_baseline"] == pytest.approx(0.1)          # 100/1000
    assert test_row["spanish_trend_adjustment"] == pytest.approx(1.2)
    assert test_row["r_expected_settled"] == pytest.approx(0.12)         # 0.1 * 1.2

    # residual = 200 - 0.12*1000 = 80; r_cohort = 80/200 = 0.4; ratio = 0.4/0.12
    assert test_row["r_cohort_implied"] == pytest.approx(0.4)
    assert test_row["rate_ratio"] == pytest.approx(10 / 3)

    # The pre-B43 frozen-baseline equivalent (trend=1) would have given:
    # residual = 200 - 0.1*1000 = 100; ratio = (100/200)/0.1 = 5.0 -- larger.
    assert test_row["rate_ratio"] < 5.0


def test_negative_residual_marked_undefined_not_below_baseline(monkeypatch):
    monkeypatch.setattr(m, "TEST_YEARS", [2022])
    stock_by_year = {2016: 900, 2019: 1000, 2022: 1200}
    crime_by_year = {2019: (100, "high"), 2022: (150, "high")}
    spanish_data = {
        2019: {"spanish_male_count": 500.0, "total_perp": 0, "foreign_total": 0},
        2022: {"spanish_male_count": 1000.0, "total_perp": 0, "foreign_total": 0},
    }
    spanish_male_pop = {2019: 100000.0, 2022: 100000.0}
    # spanish_rate 2019=0.005, 2022=0.01 -> trend=2.0, r_expected_settled=0.2
    # residual = 150 - 0.2*1000 = -50 (negative -- not a valid rate)

    rows = m.run_test_b("TESTGRP", "TG", stock_by_year, crime_by_year, [2019],
                         "baseline_label", spanish_data, spanish_male_pop)
    test_row = next(r for r in rows if r["role"] == "test")

    assert test_row["r_cohort_implied"] < 0
    assert test_row["hypothesis_call"].startswith("undefined")
