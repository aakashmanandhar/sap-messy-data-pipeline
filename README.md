# SAP Messy Data Pipeline

A real, working medallion-architecture data pipeline: messy SAP-style sales
order data, generated in PostgreSQL, flowing through Google Cloud Platform
via Terraform-provisioned infrastructure, cleaned and aggregated with dbt.

## Architecture

## What's actually here

- **`generate_sap_data.py`** - generates ~300 SAP-style sales order records
  with realistic data quality issues (duplicates, inconsistent country
  naming, missing customer names, genuine returns) and inserts them into
  PostgreSQL
- **`extract_to_bronze.py`** - reads the raw messy data from PostgreSQL and
  loads it into BigQuery Bronze, exactly as-is
- **`terraform/`** - provisions all GCP infrastructure as code: three
  BigQuery datasets (Bronze/Silver/Gold), the Bronze table schema, and a
  least-privilege service account. Terraform owns infrastructure shape only
  - it never owns table contents or transformation logic
- **`dbt/`** - owns all transformation logic and data-quality tests:
  - `models/silver/silver_sales_orders.sql` - deduplicates by order ID,
    casts text fields to real numbers and dates, standardizes country
    codes, flags returns
  - `models/gold/gold_revenue_by_country.sql` - aggregates into net revenue
    by country and month, with a sales/returns breakdown
  - Both models have passing dbt tests: uniqueness, non-null checks, and
    accepted-values validation

## Why the data is deliberately messy

Real SAP exports are rarely clean. This project intentionally recreates
common real-world data quality problems so the cleaning logic solves an
actual problem, not a toy one:
- ~4% duplicate order numbers
- Inconsistent country naming (`DE`, `Germany`, `Deutschland` all appear
  for the same country)
- ~2% missing customer names
- ~6% genuine returns, represented as negative order amounts

## Setup

### Prerequisites
- PostgreSQL running locally
- A GCP project with billing enabled
- Python 3.12 (dbt does not yet support 3.14 - see note below)
- Terraform installed and authenticated (`gcloud auth application-default login`)

### 1. PostgreSQL
Create a database `sap_messy_data` with:
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

### 2. Python environment
This project uses Python 3.12 specifically, since dbt-core does not yet
support 3.14 (a `mashumaro`/`pydantic` incompatibility as of this writing).
```bash
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment variables
Create a `.env` file (not committed) with:

### 4. Generate the messy source data
```bash
python generate_sap_data.py
```

### 5. Provision GCP infrastructure
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # add your real project_id
terraform init
terraform apply
```

Extract the generated service account key:
```powershell
$keysPath = Join-Path (Split-Path (Get-Location) -Parent) "keys\dbt_service_account.json"
$encoded = terraform output -raw pipeline_sa_key_base64
[System.IO.File]::WriteAllBytes($keysPath, [System.Convert]::FromBase64String($encoded))
```

### 6. Extract PostgreSQL data into BigQuery Bronze
```bash
cd ..
python extract_to_bronze.py
```

### 7. Set up dbt's connection profile
Create `dbt/profiles.yml` (not committed) with your project ID and the
key file path - see `dbt/profiles.yml` structure in the project for the
exact format.

### 8. Run the transformations
```bash
cd dbt
dbt run
dbt test
```

## What's next

- Orchestration: wrapping the extraction and dbt steps in an Airflow DAG,
  running in Docker (Airflow does not run reliably natively on Windows)
- CI/CD: validating Terraform and dbt on every push via GitHub Actions