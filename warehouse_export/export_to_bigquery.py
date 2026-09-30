import sys
import logging

import pandas as pd
from sqlalchemy import create_engine
from google.cloud import bigquery
from google.oauth2 import service_account

from warehouse_export.config import (
    NEON_DB_URL,
    TABLE_NAME,
    BQ_PROJECT_ID,
    BQ_DATASET,
    BQ_TABLE,
    BQ_KEYFILE_PATH,
    BQ_WRITE_DISPOSITION,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def read_data_from_neon() -> pd.DataFrame:
    if not NEON_DB_URL:
        raise ValueError("NEON_DB_URL is not set. Check your .env file.")

    logger.info(f"Connecting to Neon, reading table '{TABLE_NAME}'...")
    engine = create_engine(NEON_DB_URL)

    try:
        df = pd.read_sql_table(TABLE_NAME, con=engine)
    finally:
        engine.dispose()

    if df.empty:
        raise ValueError(f"No rows found in '{TABLE_NAME}'. Nothing to export.")

    logger.info(f"Read {len(df)} rows, {len(df.columns)} columns from Neon.")
    return df


def get_bigquery_client() -> bigquery.Client:
    if not BQ_KEYFILE_PATH:
        raise ValueError("BQ_KEYFILE_PATH is not set. Check your .env/.gcp file.")

    credentials = service_account.Credentials.from_service_account_file(BQ_KEYFILE_PATH)
    return bigquery.Client(credentials=credentials, project=BQ_PROJECT_ID)


def load_to_bigquery(df: pd.DataFrame, client: bigquery.Client) -> None:
    table_id = f"{BQ_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=BQ_WRITE_DISPOSITION,
        autodetect=True,
    )

    logger.info(f"Loading {len(df)} rows into {table_id} ({BQ_WRITE_DISPOSITION})...")
    load_job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    load_job.result()

    table = client.get_table(table_id)
    logger.info(f"Load complete. {table_id} now has {table.num_rows} rows.")


def run_export() -> None:
    try:
        df = read_data_from_neon()
        client = get_bigquery_client()
        load_to_bigquery(df, client)
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_export()