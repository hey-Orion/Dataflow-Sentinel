from pathlib import Path
import json
import pandas as pd
import pytest
import src.gold_metrics as gold


@pytest.fixture
def fake_silver_df():
    return pd.DataFrame({
        "symbol": ["AAPL", "AAPL", "BTC-USD"],
        "date": pd.to_datetime(["2026-01-08", "2026-01-10", "2026-01-10"]),
        "close": [145.0, 150.0, 42000.0],
        "volume": [900000, 1000000, 500000],
    })


@pytest.fixture
def isolated_gold_env(tmp_path, monkeypatch, fake_silver_df):
    silver_dir = tmp_path / "silver"
    gold_dir = tmp_path / "gold"
    silver_dir.mkdir()
    gold_dir.mkdir()

    # *args/**kwargs needed to support the optional logger parameter
    monkeypatch.setattr(
        gold,
        "load_all_silver_data",
        lambda *args, **kwargs: fake_silver_df,
    )

    return silver_dir, gold_dir


def test_gold_creates_output_files(isolated_gold_env):
    silver_dir, gold_dir = isolated_gold_env

    gold.run_gold_layer(silver_dir=silver_dir, gold_dir=gold_dir)

    assert (gold_dir / "aggregates.csv").exists()
    assert (gold_dir / "freshness.json").exists()


def test_gold_aggregates_schema_and_values(isolated_gold_env):
    silver_dir, gold_dir = isolated_gold_env

    gold.run_gold_layer(silver_dir, gold_dir)

    df = pd.read_csv(gold_dir / "aggregates.csv")

    expected_columns = {
        "symbol",
        "latest_date",
        "latest_close",
        "avg_7d_close",
        "avg_30d_close",
        "latest_volume",
    }
    assert expected_columns.issubset(df.columns)

    aapl = df[df["symbol"] == "AAPL"].iloc[0]
    assert aapl["latest_close"] == 150.0
    assert aapl["avg_7d_close"] == 147.5


def test_gold_freshness_contract(isolated_gold_env):
    silver_dir, gold_dir = isolated_gold_env

    gold.run_gold_layer(silver_dir, gold_dir)

    with open(gold_dir / "freshness.json") as f:
        data = json.load(f)

    assert set(data.keys()) == {"AAPL", "BTC-USD"}

    for symbol, payload in data.items():
        assert "last_date" in payload
        assert "days_stale" in payload
        assert "status" in payload
        assert payload["status"] in ("FRESH", "STALE")


def test_gold_raises_error_on_missing_files(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="Empty Silver Layer"):
        gold.load_all_silver_data(empty_dir)