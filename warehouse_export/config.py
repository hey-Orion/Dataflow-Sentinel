import os
from dotenv import load_dotenv
 
load_dotenv('.env.dbt')
 
# --- Neon (Postgres) source ---
NEON_DB_URL = os.getenv("NEON_DB_URL")
TABLE_NAME = os.getenv("TABLE_NAME", "market_data")
 
# --- BigQuery destination ---
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID", "dataflow-sentinel-dbt")
BQ_DATASET = os.getenv("BQ_DATASET", "sentinel_raw")
BQ_TABLE = os.getenv("BQ_TABLE", "metrics_raw")
BQ_KEYFILE_PATH = os.getenv("BQ_KEYFILE_PATH")
 
# --- Write behavior ---
BQ_WRITE_DISPOSITION = "WRITE_TRUNCATE"
