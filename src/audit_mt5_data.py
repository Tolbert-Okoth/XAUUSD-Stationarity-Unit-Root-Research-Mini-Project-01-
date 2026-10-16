"""MT5 Data Retrieval and Comprehensive Audit Script.

This script:
1. Connects to the local MetaTrader 5 terminal in read-only mode.
2. Retrieves historical bars for all agreed timeframes (M1, M5, M15, M30, H1, H4, D1).
3. Preserves raw data immutably in Parquet format with SHA-256 hashes and metadata sidecars.
4. Executes comprehensive data-quality checks on each timeframe.
5. Generates `reports/timeframe_inventory.csv` and comprehensive audit metrics.

Adheres strictly to quantitative research reproducibility principles.
Does NOT modify or trade on MT5.
Does NOT run inferential statistical tests (ADF, KPSS, etc.).
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import MetaTrader5 as mt5
import numpy as np
import pandas as pd

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

# Ensure project root is on sys.path for direct script execution
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_quality import (
    audit_incomplete_final_bar,
    audit_large_price_changes,
    audit_market_closures_and_gaps,
    run_full_timeframe_audit,
)


# Mapping from string to MT5 timeframe constants
MT5_TIMEFRAMES: Dict[str, int] = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}


def compute_sha256(filepath: Path) -> str:
    """Compute the SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load research configuration from TOML file."""
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def extract_and_audit() -> None:
    """Execute read-only extraction and audit of MT5 historical bars."""
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "config" / "research_config.toml"
    cfg = load_config(config_path)

    data_cfg = cfg["data"]
    symbol = data_cfg["symbol"]
    start_str = data_cfg["requested_start"]
    end_str = data_cfg["requested_end"]
    timeframes = data_cfg["timeframes"]

    raw_dir = project_root / data_cfg["raw_data_dir"]
    reports_dir = project_root / data_cfg["reports_dir"]
    raw_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Parse requested bounds
    utc_start = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=datetime.timezone.utc
    )
    utc_end = datetime.datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=datetime.timezone.utc
    )

    print("=" * 70)
    print("XAUUSD QUANTITATIVE RESEARCH LAB — DATA EXTRACTION & AUDIT")
    print("=" * 70)
    print(f"Project Root: {project_root}")
    print(f"Target Symbol: {symbol}")
    print(f"Requested Date Range: {start_str} to {end_str}")
    print(f"Target Timeframes: {', '.join(timeframes)}")
    print("-" * 70)

    # Initialize MT5
    if not mt5.initialize():
        error_code, error_desc = mt5.last_error()
        print(f"ERROR: mt5.initialize() failed: ({error_code}) {error_desc}")
        sys.exit(1)

    term_info = mt5.terminal_info()
    acc_info = mt5.account_info()
    version_info = mt5.version()

    print(f"MT5 Terminal connected: {term_info.connected}")
    print(f"Terminal build: {term_info.build}")
    print(f"Broker Company: {acc_info.company if acc_info else 'N/A'}")
    print(f"Broker Server: {acc_info.server if acc_info else 'N/A'}")

    sym_info = mt5.symbol_info(symbol)
    if sym_info is None:
        print(f"ERROR: Symbol '{symbol}' not found in broker terminal.")
        mt5.shutdown()
        sys.exit(1)

    print(f"Symbol verified: {sym_info.name} ({sym_info.description})")
    print(f"Digits: {sym_info.digits}, Point: {sym_info.point}")

    extraction_manifest: Dict[str, Any] = {
        "metadata": {
            "symbol": symbol,
            "broker_company": acc_info.company if acc_info else "Unknown",
            "broker_server": acc_info.server if acc_info else "Unknown",
            "terminal_build": term_info.build if term_info else None,
            "mt5_package_version": mt5.__version__,
            "python_executable": sys.executable,
            "python_version": sys.version,
            "extraction_timestamp_utc": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "requested_start_utc": utc_start.isoformat(),
            "requested_end_utc": utc_end.isoformat(),
        },
        "snapshots": {},
    }

    audit_rows: List[Dict[str, Any]] = []
    current_time_epoch = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    try:
        for tf_name in timeframes:
            if tf_name not in MT5_TIMEFRAMES:
                print(f"Skipping unknown timeframe: {tf_name}")
                continue

            tf_const = MT5_TIMEFRAMES[tf_name]
            print(f"\nFetching {symbol} [{tf_name}]...")

            rates = mt5.copy_rates_range(symbol, tf_const, utc_start, utc_end)
            if rates is None or len(rates) == 0:
                print(f"WARNING: No bars returned for {tf_name}")
                continue

            df = pd.DataFrame(rates)
            raw_parquet_path = raw_dir / f"{symbol}_{tf_name}.parquet"

            if raw_parquet_path.exists():
                print(f"Preserving existing raw snapshot at {raw_parquet_path.name}")
            else:
                df.to_parquet(raw_parquet_path, engine="pyarrow", index=False)
                print(f"Saved raw snapshot to {raw_parquet_path.name}")

            sha256_hash = compute_sha256(raw_parquet_path)

            first_epoch = int(df["time"].iloc[0])
            last_epoch = int(df["time"].iloc[-1])
            first_iso = datetime.datetime.fromtimestamp(
                first_epoch, tz=datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S UTC")
            last_iso = datetime.datetime.fromtimestamp(
                last_epoch, tz=datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S UTC")

            snapshot_meta = {
                "timeframe": tf_name,
                "file_path": str(raw_parquet_path.relative_to(project_root)),
                "file_sha256": sha256_hash,
                "file_size_bytes": os.path.getsize(raw_parquet_path),
                "total_bars": len(df),
                "first_bar_epoch": first_epoch,
                "last_bar_epoch": last_epoch,
                "first_bar_iso": first_iso,
                "last_bar_iso": last_iso,
            }
            extraction_manifest["snapshots"][tf_name] = snapshot_meta

            # Run full quality audit
            audit_res = run_full_timeframe_audit(
                df, tf_name, reference_time_epoch=current_time_epoch
            )
            audit_res["sha256"] = sha256_hash[:12] + "..."
            audit_rows.append(audit_res)

            print(
                f"  Bars: {len(df):,d} | Range: {first_iso[:10]} to {last_iso[:10]} | "
                f"Dups: {audit_res['duplicate_count']} | Monotonic: {audit_res['is_monotonic']} | "
                f"Corrupt: {audit_res['has_data_corruption']} | OHLC Valid: {audit_res['ohlc_valid']} | "
                f"Gaps (Wknd/Break/Unexplained): {audit_res['weekend_closures']}/{audit_res['daily_session_breaks']}/{audit_res['unexplained_gaps']}"
            )

    finally:
        mt5.shutdown()
        print("\nMT5 connection closed cleanly.")

    # Save manifest
    manifest_path = raw_dir / "extraction_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(extraction_manifest, f, indent=2)
    print(f"Saved extraction manifest to {manifest_path.relative_to(project_root)}")

    # Save inventory CSV
    inventory_df = pd.DataFrame(audit_rows)
    inventory_csv_path = reports_dir / "timeframe_inventory.csv"
    inventory_df.to_csv(inventory_csv_path, index=False)
    print(f"Saved timeframe inventory to {inventory_csv_path.relative_to(project_root)}")
    print("=" * 70)


if __name__ == "__main__":
    extract_and_audit()
