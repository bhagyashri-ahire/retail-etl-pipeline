"""Optional Airflow DAG that runs the pipeline daily.
Requires `pip install apache-airflow` and this repo on the Airflow PYTHONPATH."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.pipeline import run

with DAG(
    dag_id="retail_sales_etl",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
    tags=["etl", "retail"],
) as dag:
    PythonOperator(task_id="run_retail_etl", python_callable=run)
