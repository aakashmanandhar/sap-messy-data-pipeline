import psycopg2
import random
import os
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="sap_messy_data",
    user="postgres",
    password=os.environ["DB_PASSWORD"]
)
cur = conn.cursor()

country_variants = {
    "DE": ["DE", "Germany", "DE", "Deutschland", "DE"],
    "FR": ["FR", "France", "FR"],
    "IT": ["IT", "Italy", "IT"],
    "ES": ["ES", "Spain", "ES", "España"],
    "NL": ["NL", "Netherlands", "NL"],
}

customers = [
    ("1000001", "Müller GmbH"),
    ("1000002", "Dupont SA"),
    ("1000003", "Rossi Srl"),
    ("1000004", "Klein AG"),
    ("1000005", "Garcia SL"),
]

rows = []
order_counter = 4700

for i in range(300):
    cust_id, cust_name = random.choice(customers)
    country_code = random.choice(list(country_variants.keys()))
    country_display = random.choice(country_variants[country_code])

    order_counter += 1
    vbeln = f"{order_counter:010d}"

    base_date = date(2026, 6, 1) + timedelta(days=random.randint(0, 29))
    erdat = base_date.strftime("%Y%m%d")

    is_return = random.random() < 0.06
    amount = round(random.uniform(500, 25000), 2)
    if is_return:
        amount = -amount

    name_field = None if random.random() < 0.02 else cust_name

    rows.append((vbeln, cust_id, name_field, country_display, f"{amount:.2f}", "EUR", erdat))

# Add a small batch of exact duplicates, on purpose
dupes = random.sample(rows, k=int(len(rows) * 0.04))
rows.extend(dupes)
random.shuffle(rows)

print(f"Generated {len(rows)} rows, ready to insert.")

insert_query = """
    INSERT INTO sap_sales_orders (vbeln, kunnr, name1, land1, netwr, waerk, erdat)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

cur.executemany(insert_query, rows)
conn.commit()

print(f"Inserted {len(rows)} rows into sap_sales_orders.")

cur.close()
conn.close()