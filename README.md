# XAUUSD Mean-Reversion & Stationarity Research Lab
## Research Mini-Project 01

---

## Overview

This project is **Phase 1** of an educational, reproducible quantitative research investigation into the **stationarity and potential mean-reverting statistical properties** of XAUUSD (Gold vs. US Dollar) price levels over the **2024–2026** sample period.

> **This is strictly a research and education project.**
> No trading strategies, trade signals, entry/exit optimizations, or profitability claims are made.

---

## Research Question (RQ-01)

> *Does the selected XAUUSD price-level series over the 2024–2026 sample provide statistical evidence consistent with a unit-root process or a stationary alternative?*

---

## Key Findings

### 1. Executive Summary

Using **198,277 completed 5-minute (M5) Bid Close observations** from `2024-01-02 01:00 UTC` to `2026-10-16 09:35 UTC`, the Augmented Dickey–Fuller (ADF) test was applied under pre-registered specifications:

| Verdict | Detail |
|:---|:---|
| **Price Levels** | ❌ **Failed to reject** the unit-root null hypothesis under both `ct` (constant + trend) and `c` (constant only) specifications |
| **Log Returns** | ✅ **Rejected** the unit-root null hypothesis (p < 10⁻⁶) |
| **Integration Order** | Results are **consistent with I(1)** behaviour — price levels appear non-stationary while first differences (returns) appear stationary |

> **Important:** Failure to reject a unit root ≠ proof that a unit root exists. Near-unit-root or structurally-breaking stationary alternatives cannot be ruled out by a standard ADF test.

---

### 2. ADF Test Results

All tests used the Schwert (1989) maximum lag bound (k_max = 80) with optimal lag selected via AIC.

| Test | Series | Specification | N | Selected Lag | ADF Statistic | 5% Critical | p-value | Decision (α = 0.05) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1 (Primary)** | Log Bid Close (ln Pₜ) | `ct` | 198,277 | 77 | **−1.3295** | −3.4105 | **0.8804** | Fail to Reject H₀ |
| **2 (Sensitivity)** | Log Bid Close (ln Pₜ) | `c` | 198,277 | 77 | **−1.3275** | −2.8616 | **0.6165** | Fail to Reject H₀ |
| **3 (Sensitivity)** | Raw Bid Close (Pₜ) | `ct` | 198,277 | 77 | **−1.6997** | −3.4105 | **0.7510** | Fail to Reject H₀ |
| **4 (Sensitivity)** | Raw Bid Close (Pₜ) | `c` | 198,277 | 77 | **−1.1629** | −2.8616 | **0.6893** | Fail to Reject H₀ |
| **5 (Diagnostic)** | Log Returns (Δ ln Pₜ) | `c` | 198,276 | 80 | **−49.6999** | −2.8616 | **< 10⁻⁶** | **Reject H₀** |

**Interpretation:**
- All four price-level specifications (Tests 1–4) fail to reject the unit-root null at any conventional significance level.
- The log-return series (Test 5) decisively rejects the unit-root null, indicating return stationarity — a standard property of financial asset returns that does **not** imply price-level mean reversion.
- The joint pattern (non-stationary levels + stationary differences) is consistent with an **integrated process of order one, I(1)**.

---

### 3. Sample Descriptive Statistics

| Series | Count | Mean | Std Dev | Skewness | Excess Kurtosis | Jarque-Bera | Distribution |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Raw Close (Pₜ) | 198,277 | $2,370.93 | $928.58 | +0.2523 | −1.2400 | 14,807 | Non-Gaussian |
| Log Close (ln Pₜ) | 198,277 | 8.0843 | 0.2796 | −0.0332 | −1.3064 | 14,135 | Non-Gaussian |
| Log Returns (rₜ) | 198,276 | +0.00036% | 0.0780% | −0.5189 | **+51.6333** | 22,034,012 | **Fat-Tailed** |

### Price Trajectory
- **First Close:** $2,065.34 (2024-01-02 01:00 UTC)
- **Last Close:** $4,176.95 (2026-10-16 09:35 UTC)
- **Sample Minimum:** $1,985.61 (2024-02-14)
- **Sample Maximum:** $5,588.42 (2026-01-29)
- **Net Change:** **+102.24%** over the sample period
- **Peak-to-Start:** **+170.58%** (peak occurred ~8.5 months before sample end)

---

### 4. Visual Diagnostics

Four diagnostic figures were generated at 300 DPI and are saved in [`reports/figures/`](reports/figures/).

| Figure | Description |
|:---|:---|
| **Fig 1: Price Levels** | Raw Bid Close (upper) and Log Bid Close (lower) — both show a prominent upward trajectory from $2,065 → $5,588 → $4,177 |
| **Fig 2: Log Returns** | 5-minute log returns fluctuate around near-zero mean with episodic volatility clustering, no directional trend |
| **Fig 3: Return Distribution** | Empirical returns vs Gaussian benchmark — sharper central peak and substantially heavier tails than normal |
| **Fig 4: ACF Diagnostics** | *Left:* Log price autocorrelation persists near 0.99+ through 40 lags (slow decay). *Right:* Log return autocorrelation decays to within Bartlett bands after lag 1 |

---

## Data Audit Summary

### Source & Coverage
- **Instrument:** XAUUSD (Gold vs. US Dollar, Bid prices)
- **Broker:** EGM Securities Limited (MetaTrader 5 Terminal, Build 6230)
- **Study Period:** 2024-01-02 through 2026-10-16
- **Primary Timeframe:** M5 (5-minute bars)
- **Timeframes Audited:** D1, H4, H1, M30, M15, M5, M1

### Timeframe Inventory

| Timeframe | Total Bars | First Bar (UTC) | Last Bar (UTC) | Duplicates | Monotonic | Missing/NaN/Inf | OHLC Valid |
|:---:|:---:|:---|:---|:---:|:---:|:---:|:---:|
| D1 | 722 | 2024-01-02 00:00 | 2026-10-16 00:00 | 0 | ✅ Strict | 0 | ✅ |
| H4 | 4,327 | 2024-01-02 00:00 | 2026-10-16 08:00 | 0 | ✅ Strict | 0 | ✅ |
| H1 | 16,537 | 2024-01-02 01:00 | 2026-10-16 09:00 | 0 | ✅ Strict | 0 | ✅ |
| M30 | 33,054 | 2024-01-02 01:00 | 2026-10-16 09:30 | 0 | ✅ Strict | 0 | ✅ |
| M15 | 66,100 | 2024-01-02 01:00 | 2026-10-16 09:30 | 0 | ✅ Strict | 0 | ✅ |
| **M5** | **198,278** | 2024-01-02 01:00 | 2026-10-16 09:40 | 0 | ✅ Strict | 0 | ✅ |
| M1 | 990,806 | 2024-01-02 01:00 | 2026-10-16 09:42 | 0 | ✅ Strict | 0 | ✅ |

### 10-Point Data Quality Checks — All Passed ✅

1. **Observation Count & Date Range** — Verified across all 7 timeframes
2. **Duplicate Timestamps** — 0 duplicates across 1.3M+ cumulative bars
3. **Chronological Monotonicity** — Strictly monotonic increasing (no clock rollbacks)
4. **Missing/Invalid/Zero/Negative Prices** — Zero data corruption
5. **OHLC Geometric Consistency** — 100% valid (High ≥ max(O,C), Low ≤ min(O,C))
6. **Large Price Move Screening** — Max M5 move = 2.89% (below 3% audit threshold); extreme moves attributed to genuine market events
7. **Gap Decomposition** — 142 weekend closures, 556 daily session breaks, 34 holiday/maintenance gaps — all structural, not data defects
8. **Incomplete Final Bar** — Forming bar excluded from primary sample (198,277 completed bars used)
9. **Reconnaissance Cross-Check** — Counts match initial inventory (+2 M5 bars from extraction timing)
10. **Retrieval Completeness** — Full history returned; no broker rate-limiting or truncation

### Timestamp Verification
- Raw epoch timestamps are **UTC**, per official MT5 Python API documentation
- Zero timezone conversions applied — raw `int64` epoch values preserved in Parquet
- ADF test results are invariant to timestamp representation (depend only on chronological bar order)

---

## Technical Limitations & Methodological Discussion

1. **Failure to Reject ≠ Proof of Unit Root:**
   Failing to reject H₀ (p = 0.8804) means the data is *consistent with* a unit root under the specified linear model. Near-unit-root processes (e.g. ρ = 0.9998) can produce similar statistics in finite samples.

2. **Structural Breaks (Perron 1989):**
   If the true process is stationary around a trend with structural shifts, standard linear ADF has low power and is biased toward failing to reject H₀. Endogenous break-point tests would be needed to evaluate this.

3. **High-Frequency Microstructure Effects:**
   At 5-minute sampling, bid-ask bounce and transient liquidity variations introduce negative first-order autocorrelation in returns that should not be confused with economic mean reversion.

4. **Broker-Specific Quotes:**
   Data represents Bid prices from EGM Securities — spreads and quote mechanics reflect broker-specific feeds, not consolidated interbank midpoints.

5. **Scope:**
   This study does not test trading strategies, model transaction costs, evaluate market timing rules, or make profitability assertions. Failure to reject a unit root under linear ADF does not evaluate non-linear or multi-asset methodologies.

---

## Repository Layout

```
XAUUSD_MeanReversion_Lab/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   └── research_config.toml          # Research configuration & thresholds
├── data/
│   ├── raw/                          # Immutable raw Parquet snapshots & SHA-256 manifest
│   │   ├── XAUUSD_D1.parquet
│   │   ├── XAUUSD_H4.parquet
│   │   ├── XAUUSD_H1.parquet
│   │   ├── XAUUSD_M30.parquet
│   │   ├── XAUUSD_M15.parquet
│   │   ├── XAUUSD_M5.parquet
│   │   ├── XAUUSD_M1.parquet
│   │   └── extraction_manifest.json
│   └── processed/                    # Derived analysis sets
├── reports/
│   ├── figures/                      # Diagnostic charts (300 DPI)
│   │   ├── fig1_price_levels.png
│   │   ├── fig2_log_returns.png
│   │   ├── fig3_return_distribution.png
│   │   └── fig4_autocorrelation_diagnostics.png
│   ├── reconnaissance_review.md
│   ├── data_audit_report.md
│   ├── timeframe_inventory.csv
│   ├── research_protocol_draft.md
│   ├── descriptive_statistics.csv
│   ├── adf_test_results.csv
│   ├── adf_test_results.json
│   └── statistical_analysis_report.md
├── src/
│   ├── __init__.py
│   ├── data_quality.py               # Data-quality and geometric validation
│   ├── audit_mt5_data.py             # Read-only extraction and audit pipeline
│   └── statistical_analysis.py       # ADF testing, lag selection, and plotting
└── tests/
    ├── __init__.py
    ├── test_data_quality.py
    └── test_statistical_analysis.py
```

---

## Reproducibility & Execution

### Prerequisites
- Python 3.11+
- MetaTrader 5 terminal connected (for data extraction only)
- Install dependencies: `pip install -r requirements.txt`

### Commands

1. **Run Full Automated Test Suite:**
   ```powershell
   python -m pytest tests/ -v
   ```
2. **Execute Read-Only Extraction & Audit Pipeline:**
   ```powershell
   python src/audit_mt5_data.py
   ```
3. **Execute Pre-Registered Statistical Analysis & Plotting:**
   ```powershell
   python src/statistical_analysis.py
   ```

---

## Verification & Audit Trail

| Check | Status |
|:---|:---:|
| Raw Parquet snapshots preserved with SHA-256 checksums | ✅ |
| All 13 unit tests pass with zero warnings | ✅ |
| No unapproved operations (no trading, no KPSS, no cointegration) | ✅ |
| Pre-registered protocol followed exactly | ✅ |

---

## Software Environment

| Component | Version |
|:---|:---|
| Python | 3.11.0rc2 |
| statsmodels | 0.14.6 |
| scipy | 1.14.1 |
| numpy | 2.2.6 |
| MetaTrader 5 Terminal | Build 6230 |
| Broker | EGM Securities Limited |

---

## License

This project is for educational and research purposes only.
