# SAP Messy Data Pipeline (Learning Project)

This project simulates a realistic, messy SAP sales orders dataset — the
kind of raw data a real SAP system hands you before any cleaning happens —
and is the starting point for a full data engineering pipeline built for
learning purposes.

## What's here so far

- `generate_sap_data.py` — generates ~300 SAP-style sales order records and
  inserts them into a local PostgreSQL database, with realistic data quality
  issues baked in on purpose:
  - Duplicate order numbers (~4% of rows)
  - Inconsistent country naming (`DE`, `Germany`, `Deutschland` all appear
    for the same country)
  - Missing customer names (~2% of rows)
  - Genuine returns, represented as negative order amounts (~6% of rows)

## Why the data looks like this

Real SAP exports are rarely clean. Field names are cryptic (`VBELN`,
`KUNNR`, `NETWR`), country values are inconsistent depending on who entered
them, and duplicate or missing data is common. This project intentionally
recreates that mess so the cleaning logic built on top of it — deduplication,
standardization, type casting — is solving a real problem, not a toy one.

## Setup

1. PostgreSQL running locally, with a database named `sap_messy_data`
2. A table created with:
```sql
   CREATE TABLE sap_sales_orders (
       vbeln  VARCHAR(10),
       kunnr  VARCHAR(10),
       name1  VARCHAR(100),
       land1  VARCHAR(50),
       netwr  VARCHAR(20),
       waerk  VARCHAR(5),
       erdat  VARCHAR(8)
   );
```
3. A `.env` file (not committed) containing: