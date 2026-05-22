from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import json
import pandas as pd
from src.logger import get_logger


def load_all_silver_data(
    silver_dir: Path,
    logger: Optional[object] = None,
) -> pd.DataFrame:

    if logger is None:
        logger = get_logger(__name__)

    files = list(silver_dir.glob("*.csv"))

    if not files:
        logger.error(f"No silver files found in {silver_dir}")
        raise FileNotFoundError("Empty Silver Layer")

    df = pd.concat(
        [pd.read_csv(f, parse_dates=["date"]) for f in files],
        ignore_index=True,
    )

    before = len(df)
    df = df.drop_duplicates(subset=["symbol", "date"])

    if len(df) < before:
        logger.info(f"Removed {before - len(df)} duplicate rows from Silver data")

    if df.empty:
        logger.error("Silver dataset is empty after deduplication")
        raise ValueError("No usable data in Silver layer")

    return df


def compute_aggregates(
    df: pd.DataFrame,
    logger: Optional[object] = None,
) -> pd.DataFrame:

    if logger is None:
        logger = get_logger(__name__)

    logger.info("Computing gold aggregates")

    df = df.sort_values(["symbol", "date"])
    results = []

    for symbol, group in df.groupby("symbol"):
        latest = group.iloc[-1]
        results.append({
            "symbol": symbol,
            "latest_date": latest["date"].date().isoformat(),
            "latest_close": float(latest["close"]),
            "avg_7d_close": float(group["close"].tail(7).mean()),
            "avg_30d_close": float(group["close"].tail(30).mean()),
            "latest_volume": int(latest["volume"]),
        })

    return pd.DataFrame(results)


def compute_data_freshness(df: pd.DataFrame) -> dict:
    today = datetime.now(timezone.utc).date()
    freshness = {}

    for symbol, group in df.groupby("symbol"):
        last_date = group["date"].max().date()
        days_since = (today - last_date).days

        freshness[symbol] = {
            "last_date": last_date.isoformat(),
            "days_stale": days_since,
            "status": "STALE" if days_since > 2 else "FRESH",
        }

    return freshness


def run_gold_layer(
    silver_dir: Path,
    gold_dir: Path,
    run_id: Optional[str] = None,
) -> None:

    logger = get_logger(__name__, run_id=run_id)
    logger.info("Starting Gold Layer processing")

    gold_dir.mkdir(parents=True, exist_ok=True)

    silver_df = load_all_silver_data(silver_dir, logger)

    aggregates = compute_aggregates(silver_df, logger)
    aggregates.to_csv(gold_dir / "aggregates.csv", index=False)
    logger.info("Aggregates file written")

    freshness = compute_data_freshness(silver_df)
    with open(gold_dir / "freshness.json", "w") as f:
        json.dump(freshness, f, indent=2)

    logger.info("Gold metrics written successfully")