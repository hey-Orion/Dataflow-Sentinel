import os
import yaml
import sentry_sdk
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from src.monitoring import init_monitoring, set_run_context
from src.ingestion import ingest_all_assets
from src.validation import validate_bronze_csv, save_silver_dataframe
from src.storage import insert_silver_dataframe
from src.gold_metrics import run_gold_layer
from src.logger import get_logger

init_monitoring()

CONFIG_PATH = PROJECT_ROOT / "config" / "assets.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

try:
    config = load_config()
    BRONZE_DIR = PROJECT_ROOT / config["paths"]["bronze"]
    SILVER_DIR = PROJECT_ROOT / config["paths"]["silver"]
    GOLD_DIR   = PROJECT_ROOT / config["paths"]["gold"]
    TICKERS    = config["assets"]
except Exception as exc:
    sentry_sdk.capture_exception(exc)
    sentry_sdk.flush(timeout=5)
    raise


def run_pipeline() -> None:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    set_run_context(run_id)

    logger = get_logger(__name__, run_id=run_id)

    try:
        with sentry_sdk.start_transaction(op="pipeline_run", name=f"Run_{run_id}"):
            logger.info("Pipeline execution started")
            logger.info(f"Run ID: {run_id}")

            start_date = config.get("start_date", "2020-01-01")
            end_date = config.get("end_date") or datetime.now(timezone.utc).date().isoformat()

            logger.info(f"Context: {len(TICKERS)} assets | Timeframe: {start_date} to {end_date}")

            try:
                ingest_all_assets(
                    tickers=TICKERS,
                    start_date=start_date,
                    end_date=end_date,
                    bronze_dir=BRONZE_DIR,
                    run_id=run_id,
                )
                logger.info("Bronze layer ingestion completed")

                bronze_files = sorted(BRONZE_DIR.glob(f"*_{run_id}.csv"))

                if not bronze_files:
                    logger.warning("No raw files found for this run_id")
                else:
                    new_data_processed = False

                    for bronze_file in bronze_files:
                        try:
                            silver_df = validate_bronze_csv(bronze_file)

                            if silver_df.empty:
                                logger.info(f"No valid data in {bronze_file.name}")
                                continue

                            save_silver_dataframe(silver_df, bronze_file, SILVER_DIR)
                            insert_silver_dataframe(silver_df)

                            new_data_processed = True
                            logger.info(f"Processed {bronze_file.name}")

                        except Exception as exc:
                            logger.error(f"Failed processing {bronze_file.name}", exc_info=exc)
                            sentry_sdk.capture_exception(exc)

                    if new_data_processed:
                        run_gold_layer(silver_dir=SILVER_DIR, gold_dir=GOLD_DIR, run_id=run_id)
                        logger.info("Gold layer analytics completed")
                    else:
                        logger.info("No new data processed — skipping Gold layer")

                logger.info("Pipeline execution finished successfully")
                sentry_sdk.capture_message(f"Pipeline run {run_id}", level="info")

            except Exception as exc:
                logger.critical("Pipeline execution failed", exc_info=exc)
                sentry_sdk.capture_exception(exc)
                sentry_sdk.capture_message(f"Pipeline run {run_id} failed", level="error")
                raise
    finally:
        sentry_sdk.flush(timeout=5)


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
    finally:
        sentry_sdk.flush(timeout=5)