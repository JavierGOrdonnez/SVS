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

Also covers Test F (added 2026-07-30, user request): a fixed-calendar-cutoff
cohort/settled split (settled_pop pinned once at stock(cutoff_year - 1),
not recomputed per year like Test B's rolling window), run for cutoff in
{2022, 2024}, with the deepest available pre-cutoff baseline.
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


# ── Test F: fixed-cutoff cohort/settled split ───────────────────────────

def _test_f_fixture():
    """2020 has real crime data (65) despite being excluded (B38) --
    included deliberately so the baseline-candidate filter's exclusion is
    actually exercised, not just vacuously true because 2020 is absent."""
    stock_by_year = {2017: 800, 2018: 850, 2019: 900, 2020: 920, 2021: 950,
                      2022: 1000, 2023: 1100, 2024: 1300}
    crime_by_year = {2017: (50, "high"), 2018: (55, "high"), 2019: (60, "high"),
                      2020: (65, "high"), 2021: (70, "high"), 2022: (80, "high"),
                      2023: (90, "high"), 2024: (110, "high")}
    years = list(crime_by_year)
    spanish_data = _flat_spanish_data(years)  # trend = 1 throughout
    spanish_male_pop = {y: 100000.0 for y in years}
    return stock_by_year, crime_by_year, spanish_data, spanish_male_pop


def test_run_test_f_cutoff_2022_baseline_excludes_2020_and_pins_settled_pop():
    stock_by_year, crime_by_year, spanish_data, spanish_male_pop = _test_f_fixture()

    rows = m.run_test_f("TESTGRP", "TG", stock_by_year, crime_by_year, 2022,
                         spanish_data, spanish_male_pop)

    assert [r["year"] for r in rows] == [2022, 2023, 2024]
    for r in rows:
        assert r["baseline_years_used"] == "2017,2018,2019,2021"  # 2020 excluded (B38)
        assert r["settled_pop_male_15_59_fixed"] == 950            # stock(2021), same every row

    by_year = {r["year"]: r for r in rows}
    assert by_year[2022]["cohort_pop_male_15_59"] == 50    # 1000-950
    assert by_year[2023]["cohort_pop_male_15_59"] == 150   # 1100-950
    assert by_year[2024]["cohort_pop_male_15_59"] == 350   # 1300-950

    # Hand-derived, trend=1 throughout: r_base = (50+55+60+70)/(800+850+900+950)
    expected_r_base = 235 / 3500
    expected_r_expected_settled = expected_r_base * 1.0
    expected_residual_2022 = 80 - expected_r_expected_settled * 950
    expected_rate_ratio_2022 = (expected_residual_2022 / 50) / expected_r_expected_settled
    assert by_year[2022]["r_settled_baseline"] == pytest.approx(expected_r_base)
    assert by_year[2022]["rate_ratio"] == pytest.approx(expected_rate_ratio_2022)


def test_run_test_f_cutoff_2024_only_tests_2024_with_deeper_baseline():
    stock_by_year, crime_by_year, spanish_data, spanish_male_pop = _test_f_fixture()

    rows = m.run_test_f("TESTGRP", "TG", stock_by_year, crime_by_year, 2024,
                         spanish_data, spanish_male_pop)

    assert [r["year"] for r in rows] == [2024]  # only year >= cutoff in TEST_YEARS
    row = rows[0]
    assert row["baseline_years_used"] == "2017,2018,2019,2021,2022,2023"  # 2020 excluded
    assert row["settled_pop_male_15_59_fixed"] == 1100  # stock(2023), the pre-cutoff year
    assert row["cohort_pop_male_15_59"] == 200           # 1300-1100


def test_run_test_f_extra_stock_lands_in_cohort_not_settled():
    stock_by_year, crime_by_year, spanish_data, spanish_male_pop = _test_f_fixture()

    unadjusted = m.run_test_f("TESTGRP", "TG", stock_by_year, crime_by_year, 2022,
                               spanish_data, spanish_male_pop, extra_stock=0)
    adjusted = m.run_test_f("TESTGRP", "TG", stock_by_year, crime_by_year, 2022,
                             spanish_data, spanish_male_pop, extra_stock=40)

    by_year_unadj = {r["year"]: r for r in unadjusted}
    by_year_adj = {r["year"]: r for r in adjusted}
    for year in by_year_unadj:
        assert (by_year_adj[year]["settled_pop_male_15_59_fixed"]
                == by_year_unadj[year]["settled_pop_male_15_59_fixed"])
        assert (by_year_adj[year]["cohort_pop_male_15_59"]
                == by_year_unadj[year]["cohort_pop_male_15_59"] + 40)
