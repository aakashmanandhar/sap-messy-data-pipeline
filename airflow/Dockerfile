FROM apache/airflow:2.9.3-python3.12

USER airflow

RUN pip install --no-cache-dir \
    psycopg2-binary==2.9.9 \
    python-dotenv==1.0.1 \
    google-cloud-bigquery==3.42.2 \
    dbt-bigquery==1.11.3