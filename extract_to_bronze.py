import psycopg2
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()

pg_conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="sap_messy_data",
    user="postgres",
    password=os.environ["DB_PASSWORD"]
)
pg_cur = pg_conn.cursor()

credentials = service_account.Credentials.from_service_account_file(
    "keys/dbt_service_account.json"
)
bq_client = bigquery.Client(
    credentials=credentials,
    project="sap-postgres-pipeline"
)

pg_cur.execute("""
    SELECT vbeln, kunnr, name1, land1, netwr, waerk, erdat
    FROM sap_sales_orders
""")

rows = pg_cur.fetchall()
print(f"Fetched {len(rows)} rows from PostgreSQL.")

pg_cur.close()
pg_conn.close()

table_id = "sap-postgres-pipeline.bronze_dev.sales_orders"

rows_to_insert = [
    {
        "vbeln": row[0],
        "kunnr": row[1],
        "name1": row[2],
        "land1": row[3],
        "netwr": row[4],
        "waerk": row[5],
        "erdat": row[6],
    }
    for row in rows
]

errors = bq_client.insert_rows_json(table_id, rows_to_insert)

if errors == []:
    print(f"Successfully loaded {len(rows_to_insert)} rows into {table_id}.")
else:
    print("Errors occurred while inserting rows:")
    print(errors)