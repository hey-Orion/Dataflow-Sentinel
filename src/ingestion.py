from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import os
import pandas as pd
import yfinance as yf
from src.logger import get_logger

logger = get_logger(__name__)


def fetch_asset_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    logger.info(f"Fetching: {symbol}")
    try:
        df = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=False,
        )

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            return pd.DataFrame()

        df.reset_index(inplace=True)
        df["symbol"] = symbol
        return df

    except Exception as exc:
        logger.error(f"Error fetching {symbol}: {exc}")
        return pd.DataFrame()


def save_bronze_data(symbol: str, df: pd.DataFrame, bronze_dir: Path, run_id: str) -> str:
    os.makedirs(bronze_dir, exist_ok=True)
    file_path = bronze_dir / f"{symbol}_{run_id}.csv"
    df.to_csv(file_path, index=False)
    logger.info(f"Saved Bronze file: {file_path}")
    return str(file_path)


def ingest_all_assets(
    tickers: List[str],
    start_date: str,
    end_date: str,
    bronze_dir: Path,
    run_id: Optional[str] = None,
) -> List[str]:

    if run_id is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    saved_files = []

    for symbol in tickers:
        df = fetch_asset_data(symbol, start_date, end_date)

        if not df.empty:
            saved_files.append(save_bronze_data(symbol, df, bronze_dir, run_id))
        else:
            logger.warning(f"No data to save for {symbol}")

    return saved_files