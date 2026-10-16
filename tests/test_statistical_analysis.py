"""Unit Tests for Statistical Analysis Module.

All test series in this module are purely SYNTHETIC benchmarks with mathematically
known data-generating processes (e.g. pure random walks and Ornstein-Uhlenbeck processes).
None of these datasets represent observed market prices.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.statistical_analysis import (
    calculate_schwert_max_lag,
    compute_descriptive_statistics,
    run_adf_test,
)


def test_calculate_schwert_max_lag() -> None:
    """Test Schwert's maximum lag rule calculation."""
    # For T = 100: floor(12 * (100/100)^0.25) = 12
    assert calculate_schwert_max_lag(100) == 12
    # For T = 198,277: floor(12 * (198277/100)^0.25) = 80
    assert calculate_schwert_max_lag(198277) == 80
    # Edge case: zero or negative
    assert calculate_schwert_max_lag(0) == 0


def test_compute_descriptive_statistics_synthetic() -> None:
    """Test descriptive statistics on synthetic standard normal data."""
    np.random.seed(42)
    # 5,000 synthetic draws from N(0, 1)
    synthetic_norm = np.random.normal(loc=0.0, scale=1.0, size=5000)
    stats_dict = compute_descriptive_statistics(synthetic_norm, "Synthetic Gaussian Benchmark")

    assert stats_dict["observation_count"] == 5000
    assert np.isclose(stats_dict["mean"], 0.0, atol=0.05)
    assert np.isclose(stats_dict["std_dev"], 1.0, atol=0.05)
    assert np.isclose(stats_dict["skewness"], 0.0, atol=0.1)
    assert np.isclose(stats_dict["excess_kurtosis"], 0.0, atol=0.2)
    assert stats_dict["is_gaussian"] is True


def test_run_adf_test_synthetic_stationary_process() -> None:
    """Test ADF test on a known stationary autoregressive AR(1) process:

    y_t = 0.5 * y_{t-1} + e_t (mean-reverting, stationary |phi| < 1).
    Expectation: Reject H0 at 5% significance level.
    """
    np.random.seed(42)
    n = 1000
    e = np.random.normal(scale=1.0, size=n)
    y = np.zeros(n)
    for t in range(1, n):
        y[t] = 0.5 * y[t - 1] + e[t]

    res = run_adf_test(
        series=y,
        regression_spec="c",
        max_lag=10,
        series_name="Synthetic Stationary AR(1)",
        autolag="AIC",
    )

    assert "adf_test_statistic" in res
    assert "p_value" in res
    assert "effective_observations_nobs" in res
    assert res["effective_observations_nobs"] > 950
    # For a stationary process, ADF statistic is strongly negative, rejecting H0
    assert res["adf_test_statistic"] < res["critical_value_5pct"]
    assert res["p_value"] < 0.01
    assert res["reject_h0_5pct"] is True


def test_run_adf_test_synthetic_random_walk_with_drift() -> None:
    """Test ADF test on a known unit-root process:

    y_t = y_{t-1} + 0.05 + e_t (pure random walk with drift).
    Expectation under constant-only specification ('c'):
    Fails to reject H0 (p-value > 0.05).
    """
    np.random.seed(42)
    n = 1000
    e = np.random.normal(scale=1.0, size=n)
    y = np.cumsum(e + 0.05)

    res = run_adf_test(
        series=y,
        regression_spec="c",
        max_lag=10,
        series_name="Synthetic Unit-Root Random Walk",
        autolag="AIC",
    )

    # In levels under 'c', random walk with drift fails to reject unit root
    assert res["reject_h0_5pct"] is False
    assert res["p_value"] > 0.05
    assert res["adf_test_statistic"] > res["critical_value_5pct"]
