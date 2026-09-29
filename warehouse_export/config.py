import os
from dotenv import load_dotenv
 
load_dotenv()
 
# --- Neon (Postgres) source ---
NEON_DB_URL = os.getenv("NEON_DB_URL")  # e.g. postgresql://user:pass@host/dbname
GOLD_TABLE_NAME = os.getenv("GOLD_TABLE_NAME", "gold_metrics")  # table to export
 
# --- BigQuery destination ---
BQ_PROJECT_ID = os.getenv("BQ_PROJECT_ID", "dataflow-sentinel-dbt")
BQ_DATASET = os.getenv("BQ_DATASET", "sentinel_raw")
BQ_TABLE = os.getenv("BQ_TABLE", "gold_metrics_raw")
BQ_KEYFILE_PATH = os.getenv("BQ_KEYFILE_PATH")  # full path to the service account JSON
 
# --- Write behavior ---
# "WRITE_TRUNCATE" replaces the table each run (simplest, matches your
# idempotent-rerun principle). "WRITE_APPEND" would add rows each run instead.
BQ_WRITE_DISPOSITION = "WRITE_TRUNCATE"