# Formal Research Protocol Draft — Study RQ-01

**Project:** XAUUSD Mean-Reversion & Stationarity Research (Mini-Project 01)  
**Document Status:** DRAFT — AWAITING USER APPROVAL PRIOR TO TESTING  
**Date:** 2026-10-16  

---

## 1. Research Question

**RQ-01:**  
> *Does the selected XAUUSD price-level series over the 2024–2026 sample provide statistical evidence consistent with a unit-root process or a stationary alternative?*

---

## 2. Formal Hypotheses

### Primary Test: Augmented Dickey–Fuller (ADF) Test
The ADF test investigates whether the autoregressive polynomial of the price series possesses a root on the unit circle.

$$\Delta y_t = \alpha + \beta t + \gamma y_{t-1} + \sum_{i=1}^{k} \delta_i \Delta y_{t-i} + \varepsilon_t$$

- **Null Hypothesis ($H_0$):** $\gamma = 0$  
  *The price-level series possesses a unit root (it is non-stationary, $I(1)$ or higher). Shocks to the series are permanent and have infinite memory.*
- **Alternative Hypothesis ($H_1$):** $\gamma < 0$  
  *The price-level series is stationary (or trend-stationary). Shocks are transitory, and the series tends to revert toward a constant mean or deterministic trend.*

**Decision Threshold:** $\alpha = 0.05$ (5% significance level).

---

## 3. Predeclared Sample and Data Selection

| Parameter | Specification | Rationale |
| :--- | :--- | :--- |
| **Instrument** | `XAUUSD` (Spot Gold vs US Dollar) | Verified broker symbol |
| **Data Feed** | MetaTrader 5 (EGM Securities Limited) | Direct read-only extraction |
| **Sample Start** | `2024-01-02 01:00:00 UTC` (Bar Epoch: `1704157200`) | First regular trading bar of 2024 (Row 0) |
| **Sample End** | `2026-10-16 09:35:00 UTC` (Bar Epoch: `1792143300`) | Last completed M5 bar prior to extraction (Row 198276) |
| **Raw Snapshot Rows** | **198,278 bars** | Full preserved raw Parquet snapshot |
| **Right-Censoring Rule** | **Exclude Row 198277** (`09:40:00 UTC`, epoch `1792143600`) | Excludes active forming bar at extraction time |
| **Primary Sample Size** | **198,277 completed bars** | Rows 0 through 198276 inclusive |
| **Primary Timeframe** | **5-Minute (`M5`)** | Pre-registered primary timeframe |
| **Secondary Timeframes** | **Daily (`D1`) and 1-Hour (`H1`)** | Multi-frequency sensitivity checks |
| **Primary Price Series** | **Log Bid Close: $y_t = \ln(P_t)$** | Stabilizes variance, standard financial econometric specification |
| **Sensitivity Price Series**| **Raw Bid Close: $y_t = P_t$** | Robustness check against log transformation |
| **Secondary Diagnostic** | **First Difference Log Returns: $r_t = \Delta \ln(P_t)$** | Evaluates $I(1)$ vs $I(0)$ return properties (separate from price-level) |

---

## 4. Test Specifications & Econometric Design

### Primary ADF Specification: Constant + Linear Trend (`'ct'`)
- **Regression equation:** $\Delta y_t = \alpha + \beta t + \gamma y_{t-1} + \sum_{i=1}^{k} \delta_i \Delta y_{t-i} + \varepsilon_t$
- **Economic Rationale:** Over 2024–2026, gold experienced sustained global price appreciation. When a series has a strong upward trajectory, omitting the deterministic trend ($\beta t$) causes the ADF test to lose power and heavily bias toward falsely failing to reject the unit root. The `'ct'` specification tests for trend-stationarity (mean-reversion around a deterministic growth path).

### Sensitivity ADF Specification: Constant Only (`'c'`)
- **Regression equation:** $\Delta y_t = \alpha + \gamma y_{t-1} + \sum_{i=1}^{k} \delta_i \Delta y_{t-i} + \varepsilon_t$
- **Economic Rationale:** Tests whether price levels mean-revert around a fixed, horizontal level. If gold has secular growth, `'c'` is expected to fail to reject $H_0$. Comparing `'ct'` and `'c'` rigorously separates level mean-reversion from trend mean-reversion.

### Lag Selection & Effective Sample Size Documentation
- **Selection Criterion:** Akaike Information Criterion (**AIC**).
- **Maximum Lag Bound ($k_{\max}$):** Schwert's criterion:
  $$k_{\max} = \min\left(100, \left\lfloor 12 \times \left(\frac{T}{100}\right)^{1/4}\right\rfloor\right) = \left\lfloor 12 \times \left(\frac{198277}{100}\right)^{1/4}\right\rfloor = 80\text{ lags}$$
- **Effective Sample Size Protocol ($T_{\text{eff}}$):**
  - The actual lag $k^*$ selected by AIC from candidate lags $k \in \{0, 1, \dots, 80\}$ will be reported when tests are fitted.
  - The exact effective number of observations ($T_{\text{eff}}$) used in each regression will be recorded directly from the statistical library output (`nobs` in `statsmodels`), rather than assumed a priori. With $T = 198,277$, $T_{\text{eff}}$ is bounded between $198,196$ and $198,276$.

---

## 5. Rules for Data Integrity & Missing Values

1. **No Data Tampering:** No artificial interpolation, forward-filling, spline smoothing, or synthetic noise injection will be applied.
2. **Treatment of Weekend & Session Gaps:** In time-series econometrics of financial assets, observations are indexed by trading bar order $t = 1, 2, \dots, T$. Institutional market closures (weekends, session rolls) are treated as non-trading intervals; prices do not evolve continuously when the market is closed.
3. **Outlier Policy:** Screened large price moves will be retained in the sample. Any sensitivity check excluding extreme events must be run as an auxiliary test, never as an unrecorded modification to the primary dataset.

---

## 6. Secondary Analyses & Integration Order Clarification

1. **First-Difference / Return Stationarity:**
   - ADF will be executed on log returns: $r_t = \Delta \ln(P_t) = \ln(P_t) - \ln(P_{t-1})$.
   - **Crucial Rule:** Rejection of a unit root in returns ($r_t \sim I(0)$) is standard behavior for financial returns and does **NOT** imply that price levels $P_t$ are stationary or mean-reverting.
2. **Interpretation of Integration Order:**
   - If the primary test fails to reject $H_0$ on log prices $\ln(P_t)$, and the secondary test rejects $H_0$ on log returns $\Delta \ln(P_t)$, this constitutes **evidence consistent with an integrated process of order one ($I(1)$)**.
   - **Not Conclusive Proof:** This joint outcome is consistent with an $I(1)$ process, but does not definitively prove it. In finite samples, unit-root tests have low power against near-unit-root alternatives ($\rho \approx 0.999$), fractionally integrated processes ($I(d)$ with $0 < d < 1$), or trend-stationary processes subject to unmodeled structural breaks.
3. **Descriptive Statistics:**
   - Mean, variance, skewness, excess kurtosis, and Jarque-Bera normality testing of log returns.

---

## 7. Known Methodological Limitations

1. **Structural Breaks (Perron 1989):**  
   If the true data generating process is stationary within regimes but undergoes sudden structural shifts in mean or trend (e.g. major geopolitical escalations or interest rate cycle inflections), standard ADF tests have very low power and will falsely accept the unit-root null hypothesis.
2. **Microstructure Noise on M5:**  
   Intraday 5-minute bars are subject to bid-ask bounce, order flow imbalances, and liquidity variations. Negative autocorrelation at lag 1 in high-frequency returns is often a microstructure artifact rather than economic mean reversion.
3. **Single Broker Bid Prices:**  
   Data represents bid quotes from a single retail/CFD broker feed (EGM Securities). Institutional interbank midpoint prices may exhibit subtle differences.
4. **Statistical Rejection $\ne$ Trading Profitability:**  
   Statistical mean-reversion does not guarantee an exploitable trading edge after accounting for bid-ask spreads, broker financing costs (swaps), execution slippage, and regime shifts.

---

## 8. Criteria for Inconclusive Findings

A result will be explicitly classified as **inconclusive** if:
1. The ADF p-value falls within the borderline zone: $0.04 \le p \le 0.06$.
2. The outcome is acutely sensitive to lag selection (e.g., rejecting at lag $k$ but failing to reject at lag $k+1$).
3. The `'ct'` and `'c'` specifications yield contradictory conclusions without clear structural justification.

---

**Sign-off required:** Testing will proceed only upon explicit user confirmation of this protocol.
