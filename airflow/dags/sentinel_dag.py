from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='sentinel_pipeline',
    start_date=datetime(2026, 6, 1),
    schedule_interval='0 0 * * *',
    catchup=False,
    is_paused_upon_creation=True,
) as dag:

    # The single, focused task to execute your data engineering logic
    run_pipeline = BashOperator(
        task_id='src_pipeline',
        bash_command="cd /opt/project && python -m src.pipeline"
    )

    run_pipeline
