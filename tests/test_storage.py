import pytest
import pandas as pd
from datetime import date
from sqlalchemy import select, delete
import src.storage as storage
from src.storage import get_db_engine, market_data, insert_silver_dataframe


@pytest.fixture(scope="function")
def db_engine(monkeypatch):
    monkeypatch.setenv("TESTING", "1")

    # Reset the singleton so each test gets a fresh in-memory DB
    storage._engine = None
    return get_db_engine()


@pytest.fixture(autouse=True)
def clean_table(db_engine):
    with db_engine.begin() as conn:
        conn.execute(delete(market_data))
    yield


def test_insert_single_row(db_engine):
    df = pd.DataFrame([{
        "symbol": "AAPL",
        "date": date(2024, 1, 1),
        "open": 150.0, "high": 155.0, "low": 149.0, "close": 152.0,
        "volume": 1000000,
    }])

    insert_silver_dataframe(df)

    with db_engine.connect() as conn:
        result = conn.execute(select(market_data)).fetchall()

    assert len(result) == 1
    assert result[0].symbol == "AAPL"


def test_insert_is_idempotent(db_engine):
    df = pd.DataFrame([{
        "symbol": "BTC",
        "date": date(2024, 1, 1),
        "open": 40000.0, "high": 41000.0, "low": 39000.0, "close": 40500.0,
        "volume": 500,
    }])

    insert_silver_dataframe(df)
    insert_silver_dataframe(df)

    with db_engine.connect() as conn:
        rows = conn.execute(select(market_data)).fetchall()

    # UniqueConstraint should prevent duplicates
    assert len(rows) == 1


def test_empty_dataframe_is_noop(db_engine):
    insert_silver_dataframe(pd.DataFrame())

    with db_engine.connect() as conn:
        rows = conn.execute(select(market_data)).fetchall()

    assert len(rows) == 0


def test_insert_large_batch(db_engine):
    # 600 rows to exercise the batching logic (default batch is 500)
    records = [
        {
            "symbol": "TSLA",
            "date": date(2020, 1, 1) + pd.Timedelta(days=i),
            "open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0,
            "volume": 1000,
        }
        for i in range(600)
    ]

    insert_silver_dataframe(pd.DataFrame(records), batch_size=100)

    with db_engine.connect() as conn:
        rows = conn.execute(select(market_data)).fetchall()

    assert len(rows) == 600