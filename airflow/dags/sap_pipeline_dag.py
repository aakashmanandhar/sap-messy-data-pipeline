from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/dbt"

with DAG(
    dag_id="sap_postgres_to_bigquery_pipeline",
    description="PostgreSQL -> BigQuery Bronze -> dbt Silver -> dbt Gold, daily",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["sap", "postgres", "gcp", "medallion", "dbt"],
) as dag:

    extract_to_bronze = BashOperator(
        task_id="extract_to_bronze",
        bash_command="python /opt/airflow/extract_to_bronze.py",
    )

    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=f"cd {DBT_DIR} && dbt run --select silver_sales_orders",
    )

    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=f"cd {DBT_DIR} && dbt run --select gold_revenue_by_country",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test",
    )

    extract_to_bronze >> dbt_run_silver >> dbt_run_gold >> dbt_test