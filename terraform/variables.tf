variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP Region"
  type        = string
  default     = "us-central1"
}

variable "location" {
  description = "The GCP Location"
  type        = string
  default     = "US"
}
