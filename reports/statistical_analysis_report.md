# Quantitative Research Lab — Milestone 3 Report
## Econometric Analysis of XAUUSD Price-Level Stationarity (2024–2026)

**Project:** XAUUSD Mean-Reversion & Stationarity Research (Mini-Project 01)  
**Study Identifier:** RQ-01  
**Sample Period:** `2024-01-02 01:00:00 UTC` to `2026-10-16 09:35:00 UTC`  
**Data Frequency:** 5-Minute Bars (`M5`) — Primary Sample Size: $N = 198,277$ observations  
**Source Instrument:** `XAUUSD` (Bid Prices, MetaTrader 5 Terminal Build 6230, EGM Securities)  
**Software Environment:** `statsmodels` 0.14.6, `scipy` 1.14.1, `numpy` 2.2.6, Python 3.11.0rc2  

---

## 1. Executive Summary & Direct Answer to RQ-01

**Research Question (RQ-01):**  
> *Does the selected XAUUSD price-level series over the 2024–2026 sample provide statistical evidence consistent with a unit-root process or a stationary alternative?*

### Formal Finding:
Under the pre-registered research protocol, the empirical findings are summarized as follows:

1. **Primary Specification (Log Bid Close with Constant + Linear Trend, `'ct'`):**  
   The Augmented Dickey–Fuller test yields a test statistic of **$t = -1.3295$** ($p = 0.8804$). At the pre-registered 5% significance level ($\alpha = 0.05$), the test **fails to reject the null hypothesis of a unit root ($H_0$)**. The test statistic is algebraically greater than the 5% critical value of $-3.4105$.
2. **Sensitivity Specification (Log Bid Close with Constant Only, `'c'`):**  
   The test yields **$t = -1.3275$** ($p = 0.6165$), also **failing to reject the unit-root null hypothesis** (5% critical value: $-2.8616$).
3. **Robustness Check (Raw Price Levels, $P_t$):**  
   Raw price levels yield concordant results: $p = 0.7510$ under `'ct'` and $p = 0.6893$ under `'c'`. The logarithmic transformation did not alter the persistence properties of the series.
4. **Secondary Diagnostic (Log Returns / First Differences, $r_t = \Delta \ln P_t$):**  
   The ADF test on 5-minute log returns yields **$t = -49.7000$** ($p < 10^{-6}$), **rejecting the unit-root null hypothesis**.
5. **Joint Integration Order Interpretation:**  
   Failing to reject a unit root on log price levels while rejecting it on log returns is empirical evidence **consistent with an integrated process of order one, $I(1)$**. 

> **Important Econometric Distinctions:**  
> - **Failure to Reject $\ne$ Proof:** Failing to reject the unit-root null hypothesis on price levels indicates that the sample data does not provide sufficient statistical evidence to rule out a unit root under these linear specifications; it is **not conclusive mathematical proof** that a true unit root is present (e.g. near-unit-root or structurally breaking stationary alternatives cannot be ruled out).
> - **Return Stationarity $\ne$ Price-Level Mean Reversion:** A stationary return series ($r_t \sim I(0)$) is standard behavior in financial asset markets and **does NOT establish that price levels are stationary or mean-reverting**.

---

## 2. Formal ADF Test Results Table

All tests were estimated using the pre-registered Schwert (1989) maximum lag bound ($k_{\max} = 80$) with optimal lag length selected via the Akaike Information Criterion (AIC).

| Model ID | Series Tested | Specification | Total $T$ | Max Lag ($k_{\max}$) | Selected Lag ($k^*$) | Effective Obs ($T_{\text{eff}}$) | ADF Statistic | 1% Critical | 5% Critical | 10% Critical | p-value | Decision ($\alpha = 0.05$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Test 1 (Primary)** | **Log Bid Close ($\ln P_t$)** | **`ct`** (Const + Trend) | 198,277 | 80 | 77 | 198,199 | **-1.329473** | -3.9588 | **-3.4105** | -3.1271 | **0.880445** | **Fail to Reject $H_0$** |
| **Test 2 (Sensitivity)** | **Log Bid Close ($\ln P_t$)** | **`c`** (Const Only) | 198,277 | 80 | 77 | 198,199 | **-1.327547** | -3.4304 | **-2.8616** | -2.5668 | **0.616477** | **Fail to Reject $H_0$** |
| **Test 3 (Sensitivity)** | **Raw Bid Close ($P_t$)** | **`ct`** (Const + Trend) | 198,277 | 80 | 77 | 198,199 | **-1.699714** | -3.9588 | **-3.4105** | -3.1271 | **0.750997** | **Fail to Reject $H_0$** |
| **Test 4 (Sensitivity)** | **Raw Bid Close ($P_t$)** | **`c`** (Const Only) | 198,277 | 80 | 77 | 198,199 | **-1.162913** | -3.4304 | **-2.8616** | -2.5668 | **0.689343** | **Fail to Reject $H_0$** |
| **Test 5 (Diagnostic)** | **Log Returns ($\Delta \ln P_t$)** | **`c`** (Const Only) | 198,276 | 80 | 80 | 198,195 | **-49.699861** | -3.4304 | **-2.8616** | -2.5668 | **$< 10^{-6}$** | **Reject $H_0$** |

*Note: Results are archived machine-readably in `reports/adf_test_results.csv` and `reports/adf_test_results.json`.*

---

## 3. Sample Descriptive Statistics & Endpoint Analysis

The table below presents in-sample empirical estimates evaluated across the primary sample ($N = 198,277$). These metrics describe the observed historical realization and do not constitute population parameters or guarantees about future distributions:

| Series | Count | Mean | Std Dev | Median | IQR | Min | Max | Skewness | Excess Kurtosis | Jarque-Bera Stat | p-value | Distribution Form |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Raw Close ($P_t$)** | 198,277 | \$3,370.93 | \$928.58 | \$3,316.47 | \$1,676.73 | \$1,985.61 | \$5,588.42 | +0.2523 | -1.2400 | 14,807.0 | $< 10^{-6}$ | Non-Gaussian |
| **Log Close ($\ln P_t$)** | 198,277 | 8.0843 | 0.2796 | 8.1067 | 0.5097 | 7.5937 | 8.6285 | -0.0332 | -1.3064 | 14,135.3 | $< 10^{-6}$ | Non-Gaussian |
| **Log Returns ($r_t$)** | 198,276 | +0.00036% | 0.0780% | +0.00080% | 0.0601% | -2.1164% | +2.8446% | -0.5189 | **+51.6333** | 22,034,012 | $< 10^{-6}$ | **Fat-Tailed** |

### Verified Endpoint and Extrema Calculations:
- **First Included Close (Row 0):** \$2,065.34 (Timestamp: `2024-01-02 01:00:00 UTC`, epoch `1704157200`)
- **Last Included Close (Row 198276):** \$4,176.95 (Timestamp: `2026-10-16 09:35:00 UTC`, epoch `1792143300`)
- **Sample Minimum:** \$1,985.61 (Row 8,708, `2024-02-14 17:05:00 UTC`)
- **Sample Maximum:** \$5,588.42 (Row 147,313, `2026-01-29 01:35:00 UTC`)
- **Endpoint Percentage Change:** 
  $$\frac{P_{\text{last}} - P_{\text{first}}}{P_{\text{first}}} \times 100\% = \frac{4176.95 - 2065.34}{2065.34} \times 100\% = \mathbf{+102.24\%}$$
  *(Net percentage increase from the first included close to the last included close over the analyzed sample).*
- **Maximum-Price Comparison:** 
  $$\frac{P_{\max} - P_{\text{first}}}{P_{\text{first}}} \times 100\% = \frac{5588.42 - 2065.34}{2065.34} \times 100\% = \mathbf{+170.58\%}$$
  *(Comparison between initial price and sample peak; the peak occurred on 2026-01-29, approximately 8.5 months before the sample end date).*

### Return Distribution Notes:
- **Sample Excess Kurtosis (+51.63):** In-sample returns exhibit high leptokurtosis relative to a normal distribution (excess kurtosis of 0), indicating heavy tails in observed 5-minute price fluctuations.
- **Sample Skewness (-0.52):** In-sample returns display a mild negative asymmetry over the observed period.

---

## 4. Visual Diagnostics

All four figures were generated at 300 DPI and saved to [reports/figures/](file:///c:/Users/Tolbert%20Okoth/Quant_Reasearch/XAUUSD_MeanReversion_Lab/reports/figures/).

### Figure 1: Raw vs Log Price Levels
- **File:** [reports/figures/fig1_price_levels.png](file:///c:/Users/Tolbert%20Okoth/Quant_Reasearch/XAUUSD_MeanReversion_Lab/reports/figures/fig1_price_levels.png)
- **Diagnostic Description:** Plots raw Bid Close ($P_t$) in the upper panel and log Bid Close ($\ln P_t$) in the lower panel over the 198,277 observations. Both series display a prominent upward trajectory across the sample period, rising from \$2,065.34 to a peak of \$5,588.42 before finishing at \$4,176.95.

### Figure 2: High-Frequency Log Returns
- **File:** [reports/figures/fig2_log_returns.png](file:///c:/Users/Tolbert%20Okoth/Quant_Reasearch/XAUUSD_MeanReversion_Lab/reports/figures/fig2_log_returns.png)
- **Diagnostic Description:** The 5-minute percentage log returns ($r_t \times 100\%$) fluctuate around a near-zero sample mean ($0.000355\%$), exhibiting episodic volatility clustering (periods of elevated variance clustering together in time) without an in-sample directional trend.

### Figure 3: Empirical Return Distribution vs Gaussian Benchmark
- **File:** [reports/figures/fig3_return_distribution.png](file:///c:/Users/Tolbert%20Okoth/Quant_Reasearch/XAUUSD_MeanReversion_Lab/reports/figures/fig3_return_distribution.png)
- **Diagnostic Description:** Compares the empirical return histogram and density estimate against a Gaussian distribution fitted with sample mean and variance. The sample exhibits a higher, sharper central peak and heavier tails than the normal curve.

### Figure 4: Autocorrelation Function (ACF) Diagnostics
- **File:** [reports/figures/fig4_autocorrelation_diagnostics.png](file:///c:/Users/Tolbert%20Okoth/Quant_Reasearch/XAUUSD_MeanReversion_Lab/reports/figures/fig4_autocorrelation_diagnostics.png)
- **Diagnostic Description:** 
  - *Left Panel (Log Price Levels):* Autocorrelation coefficients persist near $0.99+$ through 40 lags, displaying slow, quasi-linear decay. While visually diagnostic of high persistence, sample ACF decay is an exploratory diagnostic aid and does not constitute proof of integration order.
  - *Right Panel (Log Returns):* Autocorrelation coefficients rapidly decay to within the Bartlett 95% confidence bands after lag 1, consistent with short memory in return innovations.

---

## 5. Technical Limitations & Methodological Discussion

1. **Failure to Reject Is Not Proof of a Unit Root:**  
   In classical inferential testing, failing to reject $H_0$ ($p = 0.8804$) indicates that the sample data is *consistent with* a unit root under the specified linear model. It does not prove that the true autoregressive parameter $\rho$ equals exactly $1.0000$. Near-unit-root processes (e.g. $\rho = 0.9998$) can produce similar test statistics in finite samples.
2. **Structural Breaks and Power Loss (Perron 1989):**  
   If the true process is stationary around a deterministic trend that underwent one or more structural shifts over 2024–2026, standard linear ADF specifications have low power and are biased toward failing to reject $H_0$. Testing models with endogenous structural breaks would be required to evaluate this possibility.
3. **High-Frequency Microstructure Effects:**  
   At a 5-minute sampling interval, order-book dynamics, bid-ask bounce, and transient liquidity variations introduce negative first-order autocorrelation in returns that should not be mistaken for economic price-level mean reversion.
4. **Broker-Specific Quotes:**  
   The underlying data represents Bid prices from EGM Securities. Spreads and quote mechanics reflect broker-specific feeds rather than consolidated interbank midpoints.
5. **Scope Limitations:**  
   This study does not test or implement trading strategies, model transaction costs, evaluate market timing rules, or make assertions regarding trading profitability. Failure to reject a unit root under linear ADF specifications indicates that linear price-level mean reversion is not supported by the sample evidence, but does not evaluate non-linear or multi-asset trading methodologies.

---

## 6. Project Verification & Audit Trail

- **Raw Parquet Snapshots:** Preserved in `data/raw/` with verified matching SHA-256 checksums (`6ecd90e64f79...` for M5).
- **Unit Testing Suite:** All 13 tests in `tests/` pass with zero warnings (`tests/test_data_quality.py` and `tests/test_statistical_analysis.py`).
- **No Unapproved Operations:** No trading strategies, cointegration tests, KPSS tests, or parameter optimizations were run.
