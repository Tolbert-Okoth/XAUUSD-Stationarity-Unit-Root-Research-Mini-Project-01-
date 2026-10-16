# Reconnaissance Review & Runtime Environment Assessment

**Project:** XAUUSD Mean-Reversion & Stationarity Research (Mini-Project 01)  
**Date:** 2026-10-16  
**Auditor:** Quantitative Research Lab Assistant  

---

## 1. Operating Environment Verification

| Attribute | Inspected Value | Status / Assessment |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Pro (64-bit AMD64) | Compliant with desktop MT5 requirements |
| **Project Workspace** | `C:\Users\Tolbert Okoth\Quant_Reasearch` | Primary research root |
| **Lab Directory** | `C:\Users\Tolbert Okoth\Quant_Reasearch\XAUUSD_MeanReversion_Lab` | Isolated project workspace |
| **Current Python Interpreter** | `C:\Users\Tolbert Okoth\AppData\Local\Programs\Python\Python311\python.exe` | Python 3.11.0rc2 (64-bit) |
| **Alternative Installed Interpreters** | `Python 3.12.10` (`C:\Users\Tolbert Okoth\AppData\Local\Programs\Python\Python312`) | Available if migration to standard final release is desired |
| **MetaTrader 5 Client** | `MetaTrader5==5.0.5735` | Official wheel, functional IPC connection |
| **MT5 Terminal** | `C:\Program Files\MetaTrader 5\terminal64.exe` | Running (Build 6230, PID 62328) |
| **Broker / Server** | EGM Securities Limited / `EGMSecurities-Demo` | Regulated demo feed, active market connection |

---

## 2. Assessment of Python 3.11.0rc2

### Finding
The active Python environment is `Python 3.11.0rc2`, a pre-release candidate built in September 2022. 

### Reproducibility Implications
1. **Binary Compatibility:** The binary wheels for `metatrader5` (5.0.5735), `pyarrow` (24.0.0), `pandas` (2.3.3), `numpy` (2.2.6), and `statsmodels` (0.14.6) are fully compatible and execute without numerical warnings or segmentation faults.
2. **Deterministic Parity:** For standard numerical computations, linear regressions, and statistical tests in `statsmodels`, Python 3.11.0rc2 produces identical numerical results to 3.11 final.
3. **Recommendation:** 
   - For Milestone 2 extraction and data audit, Python 3.11.0rc2 is completely suitable and has been preserved without modifying system installations.
   - If the user prefers a production-grade virtual environment for future long-term archival, a project-local virtual environment (`.venv`) can be initialized using the installed `Python 3.12.10` or a standard stable release upon explicit request.

---

## 3. Data-Access Route & Symbol Verification

- **Direct IPC Access:** Communication between Python and the MT5 terminal occurs via Windows shared memory/IPC using `mt5.initialize()`. No manual CSV export was required.
- **Symbol Confirmation:** The broker's symbol for spot Gold against the US Dollar is literally `XAUUSD`.
  - Description: `Gold vs US Dollar`
  - Digits: `2` (quote step $0.01)
  - Point: `0.01`
  - Trade Mode: Full access (market open and updating)
- **Data Pricing:** Rates extracted via `copy_rates_range` represent **broker Bid prices** (Open, High, Low, Close).

---

## 4. Preservation Strategy

All historical bars extracted from MT5 have been written as immutable, read-only Parquet files with SHA-256 integrity checksums under `data/raw/`. An accompanying JSON manifest (`data/raw/extraction_manifest.json`) records the terminal build, broker identity, extraction timestamps, and file checksums.
