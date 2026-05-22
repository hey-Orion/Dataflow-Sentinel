from pathlib import Path
from datetime import date, datetime, timezone
from typing import List
import pandas as pd
from pydantic import BaseModel, ValidationError, Field
from src.logger import get_logger

logger = get_logger(__name__)


class MarketDataRow(BaseModel):
    symbol: str = Field(min_length=1)
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


def validate_bronze_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    valid_rows: List[dict] = []
    rejected = 0

    for _, row in df.iterrows():
        try:
            # yfinance uses title-case columns (Date, Open, etc.) — map to our lowercase schema
            record = MarketDataRow(
                symbol=row["symbol"],
                date=row["Date"],
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=row["Volume"],
            )
            valid_rows.append(record.model_dump())
        except (ValidationError, KeyError, TypeError):
            rejected += 1

    silver_df = pd.DataFrame(valid_rows)
    logger.info(f"Validation complete: {len(silver_df)} passed, {rejected} rejected")
    return silver_df


def validate_bronze_csv(path: Path) -> pd.DataFrame:
    logger.info(f"Validating file: {path.name}")
    return validate_bronze_dataframe(pd.read_csv(path))


def save_silver_dataframe(df: pd.DataFrame, source_file: Path, silver_dir: Path) -> Path:
    silver_dir.mkdir(parents=True, exist_ok=True)
    run_date = datetime.now(timezone.utc).date().isoformat()
    output_path = silver_dir / f"{source_file.stem}_silver_{run_date}.csv"

    df.to_csv(output_path, index=False)
    logger.info(f"Silver file saved: {output_path.name}")
    return output_path