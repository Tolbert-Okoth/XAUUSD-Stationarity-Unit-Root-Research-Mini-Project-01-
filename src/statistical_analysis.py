"""Statistical Analysis Module for Stationarity and Unit-Root Testing.

Conducts rigorous econometric analysis of financial price series:
- Augmented Dickey-Fuller (ADF) testing under pre-specified specifications ('ct' and 'c')
- Akaike Information Criterion (AIC) optimal lag selection with Schwert's bound
- Extraction of effective sample size (nobs), test statistics, p-values, critical values
- Descriptive statistics and higher moments (skewness, kurtosis, Jarque-Bera)
- Diagnostic plotting with clear sample labels and formatting

Strictly preserves raw data as read-only.
Does NOT execute trading strategies, parameter optimizations, or forecast simulations.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless figure generation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
from statsmodels.tsa.stattools import adfuller, acf

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def calculate_schwert_max_lag(n_obs: int) -> int:
    """Calculate maximum lag length using Schwert's (1989) formula:

    k_max = floor(12 * (T / 100)^(1/4))
    Capped at 100 lags for computational stability.
    """
    if n_obs <= 0:
        return 0
    k = int(np.floor(12.0 * ((n_obs / 100.0) ** 0.25)))
    return min(100, max(1, k))


def run_adf_test(
    series: np.ndarray,
    regression_spec: str,
    max_lag: int,
    series_name: str,
    autolag: str = "AIC",
) -> Dict[str, Any]:
    """Execute Augmented Dickey-Fuller test using statsmodels.

    Parameters
    ----------
    series : np.ndarray
        1D price or return series.
    regression_spec : str
        'ct' for constant plus linear trend, 'c' for constant only.
    max_lag : int
        Maximum lag bound for autolag selection.
    series_name : str
        Descriptive identifier for the tested series.
    autolag : str
        Lag selection criterion (default 'AIC').

    Returns
    -------
    Dict[str, Any]
        Complete econometric test results and metadata.
    """
    clean_series = np.asarray(series, dtype=float)
    clean_series = clean_series[np.isfinite(clean_series)]
    raw_n_obs = len(clean_series)

    # Execute ADF test
    adf_res = adfuller(
        clean_series,
        maxlag=max_lag,
        regression=regression_spec,
        autolag=autolag,
    )

    test_stat: float = float(adf_res[0])
    p_value: float = float(adf_res[1])
    used_lag: int = int(adf_res[2])
    nobs_eff: int = int(adf_res[3])
    crit_vals: Dict[str, float] = {k: float(v) for k, v in adf_res[4].items()}
    ic_best: float = float(adf_res[5])

    # 5% significance decision
    reject_h0_5pct = bool(p_value < 0.05)
    crit_5pct = crit_vals.get("5%", np.nan)

    return {
        "series_name": series_name,
        "regression_specification": regression_spec,
        "sample_size_T": raw_n_obs,
        "max_lag_bound": max_lag,
        "selected_lag_k": used_lag,
        "effective_observations_nobs": nobs_eff,
        "adf_test_statistic": round(test_stat, 6),
        "p_value": round(p_value, 6),
        "critical_value_1pct": round(crit_vals.get("1%", np.nan), 4),
        "critical_value_5pct": round(crit_5pct, 4),
        "critical_value_10pct": round(crit_vals.get("10%", np.nan), 4),
        "ic_best_value": round(ic_best, 2),
        "reject_h0_5pct": reject_h0_5pct,
        "software_versions": {
            "statsmodels": statsmodels.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }


def compute_descriptive_statistics(series: np.ndarray, series_name: str) -> Dict[str, Any]:
    """Compute comprehensive descriptive statistics and distribution metrics."""
    s = np.asarray(series, dtype=float)
    s = s[np.isfinite(s)]
    n = len(s)

    mean_val = float(np.mean(s))
    std_val = float(np.std(s, ddof=1))
    median_val = float(np.median(s))
    min_val = float(np.min(s))
    max_val = float(np.max(s))
    q25, q75 = float(np.percentile(s, 25)), float(np.percentile(s, 75))
    iqr_val = q75 - q25

    skew_val = float(stats.skew(s))
    kurt_val = float(stats.kurtosis(s, fisher=True))  # Excess kurtosis (normal = 0)

    # Jarque-Bera normality test
    jb_stat, jb_pval = stats.jarque_bera(s)

    return {
        "series_name": series_name,
        "observation_count": n,
        "mean": round(mean_val, 8),
        "std_dev": round(std_val, 8),
        "median": round(median_val, 6),
        "iqr": round(iqr_val, 6),
        "min": round(min_val, 6),
        "max": round(max_val, 6),
        "skewness": round(skew_val, 4),
        "excess_kurtosis": round(kurt_val, 4),
        "jarque_bera_stat": round(float(jb_stat), 2),
        "jarque_bera_pvalue": float(jb_pval),
        "is_gaussian": bool(jb_pval > 0.05),
    }


def generate_diagnostic_plots(
    df_sample: pd.DataFrame,
    figures_dir: Path,
) -> List[Path]:
    r"""Generate high-resolution, labeled scientific figures for Milestone 3 reporting.

    Figures generated:
    1. fig1_price_levels.png: Raw price ($P_t$) and Log price ($\ln P_t$)
    2. fig2_log_returns.png: High-frequency 5-minute Log returns ($r_t = \Delta \ln P_t$)
    3. fig3_return_distribution.png: Histogram & KDE vs Gaussian distribution
    4. fig4_autocorrelation_diagnostics.png: ACF of log prices vs log returns
    """
    figures_dir.mkdir(parents=True, exist_ok=True)
    generated_paths: List[Path] = []

    prices = df_sample["close"].to_numpy(dtype=float)
    log_prices = np.log(prices)
    log_returns = np.diff(log_prices)
    n_obs = len(prices)

    time_indices = np.arange(n_obs)

    # Common styling
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.size"] = 10

    # -------------------------------------------------------------
    # Figure 1: Price Levels (Raw vs Log)
    # -------------------------------------------------------------
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax1.plot(time_indices, prices, color="#1f77b4", linewidth=0.8, label="Raw Bid Close ($P_t$)")
    ax1.set_title("XAUUSD 5-Minute Price Levels: 2024–2026 Primary Sample (N = 198,277)", fontsize=13, fontweight="bold")
    ax1.set_ylabel("USD per Troy Ounce", fontsize=11)
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle="--", alpha=0.6)

    ax2.plot(time_indices, log_prices, color="#ff7f0e", linewidth=0.8, label=r"Log Bid Close ($y_t = \ln P_t$)")
    ax2.set_title(r"Log Price Level: Variance-Stabilized Series ($y_t = \ln P_t$)", fontsize=12)
    ax2.set_xlabel("Sequential Bar Index (t = 0 to 198,276)", fontsize=11)
    ax2.set_ylabel(r"$\ln(\text{Price})$", fontsize=11)
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle="--", alpha=0.6)

    fig1.tight_layout()
    fig1_path = figures_dir / "fig1_price_levels.png"
    fig1.savefig(fig1_path, dpi=300)
    plt.close(fig1)
    generated_paths.append(fig1_path)

    # -------------------------------------------------------------
    # Figure 2: Log Returns
    # -------------------------------------------------------------
    fig2, ax = plt.subplots(figsize=(12, 5))
    ax.plot(time_indices[1:], log_returns * 100.0, color="#2ca02c", linewidth=0.5, alpha=0.85)
    ax.axhline(0, color="black", linestyle="-", linewidth=0.8, alpha=0.7)
    ax.set_title(r"XAUUSD 5-Minute Log Returns ($r_t = \Delta \ln P_t \times 100\%$, N = 198,276)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Sequential Bar Index (t = 1 to 198,276)", fontsize=11)
    ax.set_ylabel("Percentage Return (%)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.6)

    fig2.tight_layout()
    fig2_path = figures_dir / "fig2_log_returns.png"
    fig2.savefig(fig2_path, dpi=300)
    plt.close(fig2)
    generated_paths.append(fig2_path)

    # -------------------------------------------------------------
    # Figure 3: Return Distribution vs Gaussian Benchmark
    # -------------------------------------------------------------
    fig3, ax = plt.subplots(figsize=(10, 6))
    ret_pct = log_returns * 100.0
    mu = float(np.mean(ret_pct))
    sigma = float(np.std(ret_pct, ddof=1))

    # Histogram with empirical KDE
    count, bins, _ = ax.hist(ret_pct, bins=250, density=True, alpha=0.5, color="#17becf", edgecolor="none", label="Empirical Histogram")
    
    # Gaussian theoretical curve
    x_grid = np.linspace(bins[0], bins[-1], 1000)
    gaussian_pdf = (1.0 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_grid - mu) / sigma) ** 2)
    ax.plot(x_grid, gaussian_pdf, color="#d62728", linewidth=2.0, linestyle="--", label=rf"Normal Curve ($\mu$={mu:.4f}%, $\sigma$={sigma:.4f}%)")

    ax.set_xlim(-1.5, 1.5)  # Focus on primary density mass
    ax.set_title("Empirical Distribution of 5-Minute Log Returns vs Gaussian Benchmark", fontsize=13, fontweight="bold")
    ax.set_xlabel("5-Minute Log Return (%)", fontsize=11)
    ax.set_ylabel("Probability Density", fontsize=11)
    ax.legend(loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.6)

    fig3.tight_layout()
    fig3_path = figures_dir / "fig3_return_distribution.png"
    fig3.savefig(fig3_path, dpi=300)
    plt.close(fig3)
    generated_paths.append(fig3_path)

    # -------------------------------------------------------------
    # Figure 4: Autocorrelation Function (ACF) Diagnostics
    # -------------------------------------------------------------
    fig4, (ax_acf1, ax_acf2) = plt.subplots(1, 2, figsize=(14, 5))
    nlags = 40
    acf_prices = acf(log_prices, nlags=nlags, fft=True)
    acf_returns = acf(log_returns, nlags=nlags, fft=True)
    lag_indices = np.arange(nlags + 1)
    ci = 1.96 / np.sqrt(n_obs)

    # Price ACF
    ax_acf1.stem(lag_indices, acf_prices)
    ax_acf1.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax_acf1.axhline(ci, color="red", linestyle="--", linewidth=0.8, label="95% Bartlett CI")
    ax_acf1.axhline(-ci, color="red", linestyle="--", linewidth=0.8)
    ax_acf1.set_title(r"ACF: Log Price Level ($\ln P_t$)", fontsize=12, fontweight="bold")
    ax_acf1.set_xlabel("Lag (k)", fontsize=10)
    ax_acf1.set_ylabel("Autocorrelation", fontsize=10)
    ax_acf1.set_ylim(-0.1, 1.05)
    ax_acf1.legend(loc="upper right")
    ax_acf1.grid(True, linestyle="--", alpha=0.6)

    # Return ACF
    ax_acf2.stem(lag_indices, acf_returns)
    ax_acf2.axhline(0, color="black", linestyle="-", linewidth=0.8)
    ax_acf2.axhline(ci, color="red", linestyle="--", linewidth=0.8, label="95% Bartlett CI")
    ax_acf2.axhline(-ci, color="red", linestyle="--", linewidth=0.8)
    ax_acf2.set_title(r"ACF: Log Returns ($r_t = \Delta \ln P_t$)", fontsize=12, fontweight="bold")
    ax_acf2.set_xlabel("Lag (k)", fontsize=10)
    ax_acf2.set_ylabel("Autocorrelation", fontsize=10)
    ax_acf2.set_ylim(-0.15, 0.15)
    ax_acf2.legend(loc="upper right")
    ax_acf2.grid(True, linestyle="--", alpha=0.6)

    fig4.tight_layout()
    fig4_path = figures_dir / "fig4_autocorrelation_diagnostics.png"
    fig4.savefig(fig4_path, dpi=300)
    plt.close(fig4)
    generated_paths.append(fig4_path)

    return generated_paths


def execute_milestone3_analysis() -> Dict[str, Any]:
    """Execute complete Milestone 3 statistical testing and reporting."""
    raw_path = project_root / "data" / "raw" / "XAUUSD_M5.parquet"
    reports_dir = project_root / "reports"
    figures_dir = reports_dir / "figures"
    reports_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("XAUUSD QUANTITATIVE RESEARCH LAB — MILESTONE 3 STATISTICAL ANALYSIS")
    print("=" * 70)

    # Load raw snapshot in read-only mode
    df_raw = pd.read_parquet(raw_path)
    raw_count = len(df_raw)
    print(f"Loaded raw snapshot from: {raw_path.relative_to(project_root)}")
    print(f"Total raw observations: {raw_count:,d}")

    # Enforce pre-registered right-censoring rule: exclude the final forming bar
    df_sample = df_raw.iloc[:-1].copy()
    n_sample = len(df_sample)
    print(f"Applied final-bar exclusion rule. Primary sample size: {n_sample:,d}")
    assert n_sample == 198277, f"Expected 198,277 bars, found {n_sample}"

    # Extract price vectors
    raw_prices = df_sample["close"].to_numpy(dtype=float)
    log_prices = np.log(raw_prices)
    log_returns = np.diff(log_prices)

    # Compute maximum lag via Schwert's criterion
    k_max = calculate_schwert_max_lag(n_sample)
    print(f"Schwert (1989) maximum lag bound (k_max): {k_max} lags")

    # -------------------------------------------------------------
    # 1. Descriptive Statistics
    # -------------------------------------------------------------
    print("\nComputing descriptive statistics...")
    desc_raw = compute_descriptive_statistics(raw_prices, "Raw Bid Close ($P_t$)")
    desc_log = compute_descriptive_statistics(log_prices, r"Log Bid Close ($y_t = \ln P_t$)")
    desc_ret = compute_descriptive_statistics(log_returns, r"Log Returns ($r_t = \Delta \ln P_t$)")

    desc_table = pd.DataFrame([desc_raw, desc_log, desc_ret])
    desc_csv_path = reports_dir / "descriptive_statistics.csv"
    desc_table.to_csv(desc_csv_path, index=False)
    print(f"Saved descriptive statistics to: {desc_csv_path.relative_to(project_root)}")

    # -------------------------------------------------------------
    # 2. Augmented Dickey-Fuller (ADF) Testing Suite
    # -------------------------------------------------------------
    print("\nExecuting Augmented Dickey-Fuller tests (autolag='AIC', maxlag=80)...")
    adf_results: List[Dict[str, Any]] = []

    # Test 1: Primary - Log Bid Close, Constant + Linear Trend ('ct')
    print("  Running Test 1 (Primary): Log Bid Close ['ct']...")
    res_log_ct = run_adf_test(log_prices, regression_spec="ct", max_lag=k_max, series_name="Log Bid Close (Primary)")
    adf_results.append(res_log_ct)

    # Test 2: Sensitivity - Log Bid Close, Constant Only ('c')
    print("  Running Test 2 (Sensitivity): Log Bid Close ['c']...")
    res_log_c = run_adf_test(log_prices, regression_spec="c", max_lag=k_max, series_name="Log Bid Close (Sensitivity)")
    adf_results.append(res_log_c)

    # Test 3: Sensitivity - Raw Bid Close, Constant + Linear Trend ('ct')
    print("  Running Test 3 (Sensitivity): Raw Bid Close ['ct']...")
    res_raw_ct = run_adf_test(raw_prices, regression_spec="ct", max_lag=k_max, series_name="Raw Bid Close (Sensitivity)")
    adf_results.append(res_raw_ct)

    # Test 4: Sensitivity - Raw Bid Close, Constant Only ('c')
    print("  Running Test 4 (Sensitivity): Raw Bid Close ['c']...")
    res_raw_c = run_adf_test(raw_prices, regression_spec="c", max_lag=k_max, series_name="Raw Bid Close (Sensitivity)")
    adf_results.append(res_raw_c)

    # Test 5: Secondary Diagnostic - First Differences / Log Returns ('c')
    print("  Running Test 5 (Secondary Diagnostic): First Differences of Log Prices ['c']...")
    res_ret_c = run_adf_test(log_returns, regression_spec="c", max_lag=k_max, series_name="First Differences (Log Returns Diagnostic)")
    adf_results.append(res_ret_c)

    # Save ADF results table
    adf_df = pd.DataFrame(adf_results)
    adf_csv_path = reports_dir / "adf_test_results.csv"
    adf_json_path = reports_dir / "adf_test_results.json"
    adf_df.to_csv(adf_csv_path, index=False)
    with open(adf_json_path, "w", encoding="utf-8") as f:
        json.dump(adf_results, f, indent=2)
    print(f"Saved ADF test results to: {adf_csv_path.relative_to(project_root)}")

    # -------------------------------------------------------------
    # 3. Scientific Visualizations
    # -------------------------------------------------------------
    print("\nGenerating diagnostic figures...")
    fig_paths = generate_diagnostic_plots(df_sample, figures_dir)
    for p in fig_paths:
        print(f"  Generated figure: {p.relative_to(project_root)}")

    print("\nStatistical execution completed cleanly.")
    print("=" * 70)

    return {
        "descriptive_statistics": [desc_raw, desc_log, desc_ret],
        "adf_results": adf_results,
        "figures": [str(p.relative_to(project_root)) for p in fig_paths],
    }


if __name__ == "__main__":
    execute_milestone3_analysis()
