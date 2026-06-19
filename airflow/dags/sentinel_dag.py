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

    run_tests = BashOperator(
        task_id='tests',
        bash_command='cd /opt/project && python -m pytest -v tests/',
    )

    run_pipeline = BashOperator(
        task_id='src_pipeline',
        bash_command='cd /opt/project && python -m src.pipeline',
    )

    run_tests >> run_pipeline