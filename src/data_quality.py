"""Data Quality Audit Module for Quantitative Research.

Provides rigorous, transparent inspection functions for financial time-series data:
- Observation count and timestamp range
- Duplicate timestamp detection
- Chronological monotonicity verification
- Missing, NaN, infinite, negative, or zero price detection
- OHLC geometric consistency verification
- Large price move and return outlier screening
- Market closure vs unexplained gap classification
- Incomplete current-bar detection

All functions are non-destructive and preserve original data as read-only.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


# Nominal duration in seconds for standard MT5 timeframes
TIMEFRAME_SECONDS: Dict[str, int] = {
    "M1": 60,
    "M5": 300,
    "M15": 900,
    "M30": 1800,
    "H1": 3600,
    "H4": 14400,
    "D1": 86400,
}


def audit_observation_count_and_range(
    df: pd.DataFrame, time_col: str = "time"
) -> Dict[str, Any]:
    """Inspect observation count, start and end timestamps, and total span."""
    if df.empty:
        return {
            "total_observations": 0,
            "first_timestamp_epoch": None,
            "last_timestamp_epoch": None,
            "first_timestamp_iso": None,
            "last_timestamp_iso": None,
            "span_days": 0.0,
        }

    first_epoch = int(df[time_col].iloc[0])
    last_epoch = int(df[time_col].iloc[-1])
    span_seconds = last_epoch - first_epoch
    span_days = span_seconds / 86400.0

    first_iso = datetime.datetime.fromtimestamp(
        first_epoch, tz=datetime.timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S UTC")
    last_iso = datetime.datetime.fromtimestamp(
        last_epoch, tz=datetime.timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "total_observations": int(len(df)),
        "first_timestamp_epoch": first_epoch,
        "last_timestamp_epoch": last_epoch,
        "first_timestamp_iso": first_iso,
        "last_timestamp_iso": last_iso,
        "span_days": round(span_days, 2),
    }


def audit_duplicate_timestamps(
    df: pd.DataFrame, time_col: str = "time"
) -> Dict[str, Any]:
    """Detect any duplicate timestamps in the time-series."""
    if df.empty or time_col not in df.columns:
        return {"duplicate_count": 0, "duplicate_timestamps": []}

    duplicated_mask = df.duplicated(subset=[time_col], keep=False)
    duplicate_count = int(duplicated_mask.sum())
    sample_duplicates: List[int] = []

    if duplicate_count > 0:
        sample_duplicates = [
            int(x) for x in df.loc[duplicated_mask, time_col].unique()[:10]
        ]

    return {
        "duplicate_count": duplicate_count,
        "is_unique": duplicate_count == 0,
        "sample_duplicates": sample_duplicates,
    }


def audit_chronological_ordering(
    df: pd.DataFrame, time_col: str = "time"
) -> Dict[str, Any]:
    """Verify that timestamps are strictly monotonically increasing."""
    if df.empty or len(df) == 1:
        return {"is_monotonic_increasing": True, "inversion_count": 0}

    time_diffs = np.diff(df[time_col].to_numpy())
    inversions = np.where(time_diffs <= 0)[0]
    inversion_count = int(len(inversions))

    return {
        "is_monotonic_increasing": inversion_count == 0,
        "inversion_count": inversion_count,
        "inversion_indices": [int(idx) for idx in inversions[:10]],
    }


def audit_missing_and_invalid_values(
    df: pd.DataFrame,
    price_cols: Tuple[str, ...] = ("open", "high", "low", "close"),
    volume_cols: Tuple[str, ...] = ("tick_volume", "spread"),
) -> Dict[str, Any]:
    """Check for NaN, null, infinite, non-positive, or zero prices."""
    summary: Dict[str, Any] = {
        "nan_counts": {},
        "inf_counts": {},
        "non_positive_price_counts": {},
        "zero_price_counts": {},
        "has_data_corruption": False,
    }

    for col in price_cols:
        if col in df.columns:
            s = df[col]
            nan_cnt = int(s.isna().sum())
            inf_cnt = int(np.isinf(s.to_numpy(dtype=float)).sum())
            non_pos_cnt = int((s <= 0).sum())
            zero_cnt = int((s == 0).sum())

            summary["nan_counts"][col] = nan_cnt
            summary["inf_counts"][col] = inf_cnt
            summary["non_positive_price_counts"][col] = non_pos_cnt
            summary["zero_price_counts"][col] = zero_cnt

            if nan_cnt > 0 or inf_cnt > 0 or non_pos_cnt > 0:
                summary["has_data_corruption"] = True

    for col in volume_cols:
        if col in df.columns:
            s = df[col]
            summary["nan_counts"][col] = int(s.isna().sum())
            summary["inf_counts"][col] = int(np.isinf(s.to_numpy(dtype=float)).sum())
            # volume/spread can be zero legitimately, but cannot be negative
            neg_cnt = int((s < 0).sum())
            if neg_cnt > 0:
                summary["has_data_corruption"] = True
            summary[f"{col}_negative_count"] = neg_cnt

    return summary


def audit_ohlc_consistency(df: pd.DataFrame) -> Dict[str, Any]:
    """Verify standard geometric bounds of OHLC candles.

    Rules:
    1. High >= Open
    2. High >= Close
    3. Low <= Open
    4. Low <= Close
    5. High >= Low
    """
    required_cols = {"open", "high", "low", "close"}
    if not required_cols.issubset(df.columns) or df.empty:
        return {"all_valid": True, "total_violations": 0, "violation_breakdown": {}}

    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    open_ = df["open"].to_numpy()
    close = df["close"].to_numpy()

    # Float rounding tolerance
    eps = 1e-8

    high_lt_open = np.where((high + eps) < open_)[0]
    high_lt_close = np.where((high + eps) < close)[0]
    low_gt_open = np.where((low - eps) > open_)[0]
    low_gt_close = np.where((low - eps) > close)[0]
    high_lt_low = np.where((high + eps) < low)[0]

    breakdown = {
        "high_less_than_open": int(len(high_lt_open)),
        "high_less_than_close": int(len(high_lt_close)),
        "low_greater_than_open": int(len(low_gt_open)),
        "low_greater_than_close": int(len(low_gt_close)),
        "high_less_than_low": int(len(high_lt_low)),
    }
    total_violations = sum(breakdown.values())

    return {
        "all_valid": total_violations == 0,
        "total_violations": total_violations,
        "violation_breakdown": breakdown,
    }


def audit_large_price_changes(
    df: pd.DataFrame,
    price_col: str = "close",
    threshold_pct: float = 3.0,
    threshold_sigma: float = 5.0,
) -> Dict[str, Any]:
    """Screen for potential outlier returns and extreme single-bar price shifts.

    Note: Large returns are screened for research audit purposes only.
    They are NOT automatically removed or modified.
    """
    if df.empty or len(df) < 2 or price_col not in df.columns:
        return {
            "exceeding_pct_threshold_count": 0,
            "exceeding_sigma_threshold_count": 0,
            "max_abs_pct_return": 0.0,
            "top_moves": [],
        }

    prices = df[price_col].to_numpy(dtype=float)
    # Log returns
    log_returns = np.diff(np.log(prices))
    pct_returns = (np.diff(prices) / prices[:-1]) * 100.0

    mean_ret = float(np.mean(pct_returns))
    std_ret = float(np.std(pct_returns, ddof=1)) if len(pct_returns) > 1 else 1.0

    z_scores = np.abs((pct_returns - mean_ret) / (std_ret if std_ret > 0 else 1.0))
    abs_pct = np.abs(pct_returns)

    pct_mask = abs_pct >= threshold_pct
    sigma_mask = z_scores >= threshold_sigma

    top_idx = np.argsort(abs_pct)[::-1][:5]
    top_moves = []
    for idx in top_idx:
        bar_idx = int(idx + 1)
        t_epoch = int(df["time"].iloc[bar_idx]) if "time" in df.columns else bar_idx
        t_iso = datetime.datetime.fromtimestamp(
            t_epoch, tz=datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")
        top_moves.append(
            {
                "bar_index": bar_idx,
                "timestamp_epoch": t_epoch,
                "timestamp_iso": t_iso,
                "pct_change": round(float(pct_returns[idx]), 4),
                "z_score": round(float(z_scores[idx]), 2),
                "price_prior": round(float(prices[idx]), 2),
                "price_current": round(float(prices[idx + 1]), 2),
            }
        )

    return {
        "exceeding_pct_threshold_count": int(np.sum(pct_mask)),
        "exceeding_sigma_threshold_count": int(np.sum(sigma_mask)),
        "max_abs_pct_return": round(float(np.max(abs_pct)), 4) if len(abs_pct) > 0 else 0.0,
        "mean_pct_return": round(mean_ret, 6),
        "std_pct_return": round(std_ret, 6),
        "top_moves": top_moves,
    }


def audit_market_closures_and_gaps(
    df: pd.DataFrame,
    timeframe: str,
    time_col: str = "time",
) -> Dict[str, Any]:
    """Distinguish regular weekend/session closures from unexplained intraday gaps.

    Gold (XAUUSD) trading hours:
    - Typical weekend closure: Friday 23:59 to Sunday 23:00/Monday 00:00 (~48 hours).
    - Daily maintenance break: 23:59 to 01:00 (~1-2 hours depending on broker).
    - True gaps: intervals exceeding nominal bar spacing occurring during open trading sessions.
    """
    nominal_seconds = TIMEFRAME_SECONDS.get(timeframe, 300)
    if df.empty or len(df) < 2 or time_col not in df.columns:
        return {
            "timeframe": timeframe,
            "nominal_spacing_seconds": nominal_seconds,
            "total_gaps": 0,
            "weekend_closures": 0,
            "daily_session_breaks": 0,
            "unexplained_gaps": 0,
            "sample_unexplained_gaps": [],
        }

    times = df[time_col].to_numpy(dtype=int)
    diffs = np.diff(times)
    gap_indices = np.where(diffs > nominal_seconds)[0]

    weekend_closures = 0
    daily_breaks = 0
    unexplained_gaps = 0
    sample_unexplained: List[Dict[str, Any]] = []

    for idx in gap_indices:
        dt = int(diffs[idx])
        t_before = int(times[idx])
        t_after = int(times[idx + 1])
        dt_hours = dt / 3600.0

        # Weekend closure: typically between 40 and 60 hours
        if 40.0 <= dt_hours <= 72.0:
            weekend_closures += 1
        # Daily session roll break: between 1 and 3 hours (e.g. 3600s - 10800s)
        elif 0.9 <= dt_hours <= 3.5:
            daily_breaks += 1
        # Holiday closures: e.g. Christmas, New Year (typically 20h - 36h)
        elif 3.5 < dt_hours < 40.0:
            # Could be a full holiday closure or unexplained outage
            unexplained_gaps += 1
            if len(sample_unexplained) < 10:
                sample_unexplained.append(
                    {
                        "from_epoch": t_before,
                        "to_epoch": t_after,
                        "gap_duration_hours": round(dt_hours, 2),
                        "from_iso": datetime.datetime.fromtimestamp(
                            t_before, tz=datetime.timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "to_iso": datetime.datetime.fromtimestamp(
                            t_after, tz=datetime.timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "likely_cause": "Holiday closure or extended session break",
                    }
                )
        else:
            unexplained_gaps += 1
            if len(sample_unexplained) < 10:
                sample_unexplained.append(
                    {
                        "from_epoch": t_before,
                        "to_epoch": t_after,
                        "gap_duration_hours": round(dt_hours, 2),
                        "from_iso": datetime.datetime.fromtimestamp(
                            t_before, tz=datetime.timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "to_iso": datetime.datetime.fromtimestamp(
                            t_after, tz=datetime.timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "likely_cause": "Intraday gap or broker feed disruption",
                    }
                )

    return {
        "timeframe": timeframe,
        "nominal_spacing_seconds": nominal_seconds,
        "total_gaps": int(len(gap_indices)),
        "weekend_closures": weekend_closures,
        "daily_session_breaks": daily_breaks,
        "unexplained_gaps": unexplained_gaps,
        "sample_unexplained_gaps": sample_unexplained,
    }


def audit_incomplete_final_bar(
    df: pd.DataFrame,
    timeframe: str,
    reference_time_epoch: Optional[int] = None,
    time_col: str = "time",
) -> Dict[str, Any]:
    """Determine whether the latest bar in the dataset is incomplete (currently forming).

    A bar starting at t_open with duration T is incomplete if reference_time < t_open + T.
    Incomplete bars introduce truncation bias and must be flagged for exclusion
    prior to any inferential modeling.
    """
    if df.empty or time_col not in df.columns:
        return {"is_incomplete": False, "reason": "Empty dataset"}

    nominal_seconds = TIMEFRAME_SECONDS.get(timeframe, 300)
    last_open_epoch = int(df[time_col].iloc[-1])

    if reference_time_epoch is None:
        reference_time_epoch = int(
            datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        )

    # In MT5, if reference_time < last_open_epoch + nominal_seconds, the bar is still forming
    bar_end_epoch = last_open_epoch + nominal_seconds
    is_incomplete = reference_time_epoch < bar_end_epoch

    return {
        "timeframe": timeframe,
        "last_bar_open_epoch": last_open_epoch,
        "bar_expected_end_epoch": bar_end_epoch,
        "reference_time_epoch": reference_time_epoch,
        "is_incomplete": bool(is_incomplete),
        "last_bar_open_iso": datetime.datetime.fromtimestamp(
            last_open_epoch, tz=datetime.timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "recommendation": (
            "Exclude final incomplete bar from research sample"
            if is_incomplete
            else "Final bar is complete"
        ),
    }


def run_full_timeframe_audit(
    df: pd.DataFrame,
    timeframe: str,
    reference_time_epoch: Optional[int] = None,
) -> Dict[str, Any]:
    """Execute all data-quality audits on a single timeframe DataFrame."""
    obs_info = audit_observation_count_and_range(df)
    dups_info = audit_duplicate_timestamps(df)
    order_info = audit_chronological_ordering(df)
    invalid_info = audit_missing_and_invalid_values(df)
    ohlc_info = audit_ohlc_consistency(df)
    moves_info = audit_large_price_changes(df)
    gaps_info = audit_market_closures_and_gaps(df, timeframe)
    incomplete_info = audit_incomplete_final_bar(
        df, timeframe, reference_time_epoch=reference_time_epoch
    )

    return {
        "timeframe": timeframe,
        "observation_count": obs_info["total_observations"],
        "first_timestamp_iso": obs_info["first_timestamp_iso"],
        "last_timestamp_iso": obs_info["last_timestamp_iso"],
        "span_days": obs_info["span_days"],
        "duplicate_count": dups_info["duplicate_count"],
        "is_monotonic": order_info["is_monotonic_increasing"],
        "inversion_count": order_info["inversion_count"],
        "has_data_corruption": invalid_info["has_data_corruption"],
        "nan_counts": invalid_info["nan_counts"],
        "non_positive_price_counts": invalid_info["non_positive_price_counts"],
        "ohlc_valid": ohlc_info["all_valid"],
        "ohlc_violations": ohlc_info["total_violations"],
        "max_abs_pct_return": moves_info["max_abs_pct_return"],
        "exceeding_pct_threshold_count": moves_info["exceeding_pct_threshold_count"],
        "total_gaps": gaps_info["total_gaps"],
        "weekend_closures": gaps_info["weekend_closures"],
        "daily_session_breaks": gaps_info["daily_session_breaks"],
        "unexplained_gaps": gaps_info["unexplained_gaps"],
        "final_bar_incomplete": incomplete_info["is_incomplete"],
    }
