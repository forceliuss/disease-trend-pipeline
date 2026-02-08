terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable requisite APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "bigquery.googleapis.com",
    "composer.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# --- Service Accounts ---
resource "google_service_account" "airflow_sa" {
  account_id   = "airflow-worker"
  display_name = "Airflow Worker Service Account"
  depends_on   = [google_project_service.apis]
}

resource "google_service_account" "metabase_sa" {
  account_id   = "metabase-sa"
  display_name = "Metabase Service Account"
  depends_on   = [google_project_service.apis]
}

# --- IAM Roles ---
# Note: For production, use granular roles. 
# Airflow needs explicit roles for Composer 2
resource "google_project_iam_member" "composer_worker" {
  project = var.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:${google_service_account.airflow_sa.email}"
}

resource "google_project_iam_member" "airflow_bq_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.airflow_sa.email}"
}

resource "google_project_iam_member" "airflow_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.airflow_sa.email}"
}

# --- Storage (GCS) ---
resource "google_storage_bucket" "datalake" {
  name          = "${var.project_id}-datalake"
  location      = var.location
  force_destroy = true
  depends_on    = [google_project_service.apis]
}

resource "google_storage_bucket" "composer_bucket" {
  name          = "${var.project_id}-composer-bucket"
  location      = var.location
  force_destroy = true
  depends_on    = [google_project_service.apis]
}

# --- BigQuery Datasets ---
resource "google_bigquery_dataset" "raw_zone" {
  dataset_id = "raw_zone"
  location   = var.location
  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "staging" {
  dataset_id = "staging"
  location   = var.location
  depends_on = [google_project_service.apis]
}

resource "google_bigquery_dataset" "marts" {
  dataset_id = "marts"
  location   = var.location
  depends_on = [google_project_service.apis]
}

# --- Cloud Composer (Airflow) ---
resource "google_composer_environment" "composer" {
  name   = "disease-trend-composer"
  region = var.region

  config {
    software_config {
      image_version = "composer-2.6.0-airflow-2.7.3" 
    }

    node_config {
      service_account = google_service_account.airflow_sa.email
    }
  }

  depends_on = [
    google_project_iam_member.composer_worker,
    google_project_service.apis
  ]
}
