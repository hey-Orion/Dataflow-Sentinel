import pytest
import pandas as pd
from datetime import date
from pathlib import Path
from src.validation import (
    validate_bronze_dataframe,
    validate_bronze_csv,
    save_silver_dataframe,
)


@pytest.fixture
def valid_row_dict():
    return {
        "symbol": "AAPL",
        "Date": date(2024, 1, 1),
        "Open": 100.0, "High": 110.0, "Low": 95.0, "Close": 105.0,
        "Volume": 1_000_000,
    }


def test_valid_row_passes_validation(valid_row_dict):
    silver_df = validate_bronze_dataframe(pd.DataFrame([valid_row_dict]))

    assert len(silver_df) == 1
    assert silver_df.iloc[0]["symbol"] == "AAPL"
    assert "open" in silver_df.columns  # Silver schema uses lowercase columns


def test_invalid_symbol_is_rejected(valid_row_dict):
    valid_row_dict["symbol"] = ""  # Violates min_length=1
    silver_df = validate_bronze_dataframe(pd.DataFrame([valid_row_dict]))

    assert silver_df.empty


def test_mixed_valid_and_invalid_rows(valid_row_dict):
    bad_row = valid_row_dict.copy()
    bad_row["Date"] = "not-a-date"

    silver_df = validate_bronze_dataframe(pd.DataFrame([valid_row_dict, bad_row]))

    assert len(silver_df) == 1
    assert silver_df.iloc[0]["date"] == date(2024, 1, 1)


def test_validate_bronze_csv(tmp_path, valid_row_dict):
    bronze_file = tmp_path / "test_bronze.csv"
    pd.DataFrame([valid_row_dict]).to_csv(bronze_file, index=False)

    silver_df = validate_bronze_csv(bronze_file)

    assert not silver_df.empty
    assert "symbol" in silver_df.columns


def test_save_silver_dataframe(tmp_path):
    silver_dir = tmp_path / "silver_output"
    df = pd.DataFrame([{"symbol": "AAPL", "close": 150.0}])

    output_path = save_silver_dataframe(df, Path("AAPL_raw.csv"), silver_dir)

    assert output_path.exists()
    assert silver_dir.is_dir()
    assert "AAPL_raw_silver" in output_path.name


def test_validation_handles_missing_columns():
    # Missing most required fields — should return empty, not crash
    df = pd.DataFrame([{"symbol": "AAPL", "Date": date(2024, 1, 1)}])
    silver_df = validate_bronze_dataframe(df)

    assert silver_df.empty