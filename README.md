# XAUUSD Mean-Reversion & Stationarity Research Lab
## Research Mini-Project 01

### Overview
This project constitutes Phase 1 of an educational, reproducible quantitative research investigation into the stationarity and potential mean-reverting statistical properties of XAUUSD (Gold vs. US Dollar) price levels over the 2024–2026 sample period.

### Repository Layout
```
XAUUSD_MeanReversion_Lab/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   └── research_config.toml          # Explicit research configuration & thresholds
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
│   └── processed/                    # Derived analysis sets (empty until protocol approved)
├── reports/
│   ├── figures/                      # High-resolution diagnostic charts (DPI 300)
│   │   ├── fig1_price_levels.png
│   │   ├── fig2_log_returns.png
│   │   ├── fig3_return_distribution.png
│   │   └── fig4_autocorrelation_diagnostics.png
│   ├── reconnaissance_review.md      # Environment & MT5 connection assessment
│   ├── data_audit_report.md          # 10-point data quality & gap audit report
│   ├── timeframe_inventory.csv       # Machine-readable inventory of all 7 timeframes
│   ├── research_protocol_draft.md    # Pre-registered econometric testing protocol
│   ├── descriptive_statistics.csv    # Summary statistics for primary sample
│   ├── adf_test_results.csv          # Machine-readable ADF regression results
│   ├── adf_test_results.json         # Detailed JSON ADF metadata
│   └── statistical_analysis_report.md# Formal Milestone 3 econometric findings report
├── src/
│   ├── __init__.py
│   ├── data_quality.py               # Core data-quality and geometric validation functions
│   ├── audit_mt5_data.py             # Read-only extraction and audit pipeline
│   └── statistical_analysis.py       # ADF testing, lag selection, and plotting pipeline
└── tests/
    ├── __init__.py
    ├── test_data_quality.py          # Data-quality tests on synthetic benchmarks
    └── test_statistical_analysis.py  # Statistical tests on synthetic AR(1) & unit-root models
```

### Reproducibility & Execution
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

### Operating Rules
- Strictly non-destructive read-only interaction with MetaTrader 5.
- No trading strategies, parameter optimizations, or claims of commercial profitability.
- Statistical hypothesis testing begins only after formal protocol sign-off.
