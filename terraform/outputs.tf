output "datalake_bucket" {
  value = google_storage_bucket.datalake.name
}

output "composer_environment" {
  value = google_composer_environment.composer.name
}

output "airflow_uri" {
  value = google_composer_environment.composer.config[0].airflow_uri
}
