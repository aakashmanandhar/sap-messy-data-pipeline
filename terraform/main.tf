terraform {
  required_version = ">= 1.7.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_bigquery_dataset" "bronze" {
  dataset_id  = "bronze_dev"
  location    = var.region
  description = "Raw SAP data landed from PostgreSQL — untyped, no transformation."
}

resource "google_bigquery_dataset" "silver" {
  dataset_id  = "silver_dev"
  location    = var.region
  description = "Cleaned, typed SAP data — tables built and owned by dbt, not Terraform."
}

resource "google_bigquery_dataset" "gold" {
  dataset_id  = "gold_dev"
  location    = var.region
  description = "Business-ready aggregates — tables built and owned by dbt."
}

resource "google_service_account" "pipeline_sa" {
  account_id   = "sap-pipeline-dev"
  display_name = "SAP pipeline service account (dev)"
}

resource "google_project_iam_member" "pipeline_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "pipeline_bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_service_account_key" "pipeline_sa_key" {
  service_account_id = google_service_account.pipeline_sa.name
}