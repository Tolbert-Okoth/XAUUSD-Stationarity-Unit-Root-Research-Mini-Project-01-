"""Unit Tests for Data Quality Audit Functions.

All test datasets in this module are SYNTHETIC and explicitly constructed to test
edge cases, boundary conditions, and error-handling capabilities.
None of these datasets represent observed market prices.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data_quality import (
    audit_observation_count_and_range,
    audit_duplicate_timestamps,
    audit_chronological_ordering,
    audit_missing_and_invalid_values,
    audit_ohlc_consistency,
    audit_large_price_changes,
    audit_market_closures_and_gaps,
    audit_incomplete_final_bar,
    run_full_timeframe_audit,
)


def make_clean_synthetic_df(n: int = 100, start_epoch: int = 1704153600, step: int = 300) -> pd.DataFrame:
    """Generate a clean, geometrically valid synthetic OHLCV dataframe.

    LABEL: SYNTHETIC BENCHMARK DATA.
    """
    times = [start_epoch + i * step for i in range(n)]
    np.random.seed(42)
    # Simulated random walk for base prices
    base = 2000.0 + np.cumsum(np.random.randn(n) * 0.5)

    opens = base
    highs = base + np.abs(np.random.randn(n) * 0.4) + 0.1
    lows = base - np.abs(np.random.randn(n) * 0.4) - 0.1
    closes = base + (np.random.randn(n) * 0.2)

    # Enforce strict OHLC validity
    highs = np.maximum(highs, np.maximum(opens, closes))
    lows = np.minimum(lows, np.minimum(opens, closes))

    return pd.DataFrame({
        "time": times,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "tick_volume": [100 + i for i in range(n)],
        "spread": [15] * n,
        "real_volume": [0] * n,
    })


def test_audit_observation_count_and_range_synthetic() -> None:
    """Test observation count and epoch range on clean synthetic data."""
    df = make_clean_synthetic_df(n=50, start_epoch=1700000000, step=300)
    res = audit_observation_count_and_range(df)

    assert res["total_observations"] == 50
    assert res["first_timestamp_epoch"] == 1700000000
    assert res["last_timestamp_epoch"] == 1700000000 + 49 * 300
    assert "UTC" in res["first_timestamp_iso"]
    assert res["span_days"] > 0.0


def test_audit_duplicate_timestamps_synthetic() -> None:
    """Test detection of duplicate timestamps on synthetic data."""
    df = make_clean_synthetic_df(n=10)
    # Clean check
    clean_res = audit_duplicate_timestamps(df)
    assert clean_res["is_unique"] is True
    assert clean_res["duplicate_count"] == 0

    # Inject duplicate
    df.loc[5, "time"] = df.loc[4, "time"]
    dup_res = audit_duplicate_timestamps(df)
    assert dup_res["is_unique"] is False
    assert dup_res["duplicate_count"] == 2
    assert df.loc[4, "time"] in dup_res["sample_duplicates"]


def test_audit_chronological_ordering_synthetic() -> None:
    """Test detection of timestamp order inversions on synthetic data."""
    df = make_clean_synthetic_df(n=10)
    clean_res = audit_chronological_ordering(df)
    assert clean_res["is_monotonic_increasing"] is True
    assert clean_res["inversion_count"] == 0

    # Invert timestamps
    df.loc[6, "time"] = df.loc[4, "time"] - 100
    inv_res = audit_chronological_ordering(df)
    assert inv_res["is_monotonic_increasing"] is False
    assert inv_res["inversion_count"] >= 1


def test_audit_missing_and_invalid_values_synthetic() -> None:
    """Test detection of NaNs, infinities, negative prices, and zeros."""
    df = make_clean_synthetic_df(n=10)
    clean_res = audit_missing_and_invalid_values(df)
    assert clean_res["has_data_corruption"] is False

    # Inject corruption: NaN, Inf, Negative, Zero
    df.loc[1, "close"] = np.nan
    df.loc[2, "open"] = np.inf
    df.loc[3, "low"] = -10.0
    df.loc[4, "high"] = 0.0

    bad_res = audit_missing_and_invalid_values(df)
    assert bad_res["has_data_corruption"] is True
    assert bad_res["nan_counts"]["close"] == 1
    assert bad_res["inf_counts"]["open"] == 1
    assert bad_res["non_positive_price_counts"]["low"] == 1
    assert bad_res["zero_price_counts"]["high"] == 1


def test_audit_ohlc_consistency_synthetic() -> None:
    """Test verification of OHLC candle geometry constraints."""
    df = make_clean_synthetic_df(n=10)
    clean_res = audit_ohlc_consistency(df)
    assert clean_res["all_valid"] is True
    assert clean_res["total_violations"] == 0

    # Inject geometric violations
    # 1. High < Open
    df.loc[1, "high"] = df.loc[1, "open"] - 5.0
    # 2. Low > Close
    df.loc[2, "low"] = df.loc[2, "close"] + 5.0
    # 3. High < Low
    df.loc[3, "high"] = df.loc[3, "low"] - 1.0

    bad_res = audit_ohlc_consistency(df)
    assert bad_res["all_valid"] is False
    assert bad_res["total_violations"] >= 3
    assert bad_res["violation_breakdown"]["high_less_than_open"] >= 1
    assert bad_res["violation_breakdown"]["low_greater_than_close"] >= 1
    assert bad_res["violation_breakdown"]["high_less_than_low"] >= 1


def test_audit_large_price_changes_synthetic() -> None:
    """Test detection of large price changes and returns."""
    df = make_clean_synthetic_df(n=20)
    # Inject a 10% move between bar 9 and 10
    df.loc[10, "close"] = df.loc[9, "close"] * 1.10
    res = audit_large_price_changes(df, threshold_pct=3.0, threshold_sigma=3.0)

    assert res["exceeding_pct_threshold_count"] >= 1
    assert res["max_abs_pct_return"] >= 9.9
    assert len(res["top_moves"]) > 0
    assert res["top_moves"][0]["bar_index"] == 10


def test_audit_market_closures_and_gaps_synthetic() -> None:
    """Test classification of weekend closures, session breaks, and unexplained gaps."""
    # Create 3 bars with:
    # 1 normal step (300s)
    # 1 daily break (3600s = 1 hour)
    # 1 weekend closure (172800s = 48 hours)
    # 1 unexplained gap (18000s = 5 hours)
    t0 = 1704153600
    times = [
        t0,
        t0 + 300,             # normal
        t0 + 300 + 3600,      # daily session break (1 hour)
        t0 + 300 + 3600 + 172800,  # weekend closure (48 hours)
        t0 + 300 + 3600 + 172800 + 18000  # unexplained gap (5 hours)
    ]
    df = pd.DataFrame({
        "time": times,
        "open": [2000.0] * 5,
        "high": [2005.0] * 5,
        "low": [1995.0] * 5,
        "close": [2001.0] * 5,
        "tick_volume": [50] * 5,
        "spread": [10] * 5,
    })

    res = audit_market_closures_and_gaps(df, timeframe="M5")
    assert res["total_gaps"] == 3
    assert res["weekend_closures"] == 1
    assert res["daily_session_breaks"] == 1
    assert res["unexplained_gaps"] == 1


def test_audit_incomplete_final_bar_synthetic() -> None:
    """Test detection of forming vs closed final bar."""
    df = make_clean_synthetic_df(n=10, start_epoch=100000, step=300)
    last_open = 100000 + 9 * 300  # 102700

    # Case 1: reference time is during the bar (e.g. 102800 < 103000) -> incomplete
    res_incomplete = audit_incomplete_final_bar(
        df, timeframe="M5", reference_time_epoch=last_open + 100
    )
    assert res_incomplete["is_incomplete"] is True

    # Case 2: reference time is well past the bar (e.g. 103500 >= 103000) -> complete
    res_complete = audit_incomplete_final_bar(
        df, timeframe="M5", reference_time_epoch=last_open + 400
    )
    assert res_complete["is_incomplete"] is False


def test_run_full_timeframe_audit_synthetic() -> None:
    """Test full integration audit report generator on synthetic data."""
    df = make_clean_synthetic_df(n=30)
    summary = run_full_timeframe_audit(df, timeframe="M5")

    assert summary["timeframe"] == "M5"
    assert summary["observation_count"] == 30
    assert summary["duplicate_count"] == 0
    assert summary["is_monotonic"] is True
    assert summary["has_data_corruption"] is False
    assert summary["ohlc_valid"] is True
