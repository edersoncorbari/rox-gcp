# Provider GCP
provider "google" {
  credentials = file(var.GOOGLE_CREDENTIALS_PATH) 
  project     = var.GOOGLE_PROJECT_ID
  region      = var.GOOGLE_REGION
}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.0"
    }
  }
}

variable "GOOGLE_CREDENTIALS_PATH" {
  description = "Caminho para o arquivo de credenciais"
}

variable "GOOGLE_PROJECT_ID" {
  description = "ID do projeto do Google Cloud"
}

variable "GOOGLE_REGION" {
  description = "Região do Google Cloud"
}

variable "GOOGLE_BUCKET" {
  description = "Nome do bucket na Google Cloud"
}

# 1. Cria o bucket
resource "google_storage_bucket" "ml_models" {
  name          = var.GOOGLE_BUCKET
  location      = var.GOOGLE_REGION
  force_destroy = true
}

# 2. Cria o Cloud Composer para orquestração de pipelines
resource "google_composer_environment" "ml_composer" {
  name    = "ml-airflow"
  region  = var.GOOGLE_REGION
  config {
    software_config {
      image_version = "composer-2.11.1-airflow-2.9.3"
    }
  }
}

# 3. Cria o Vertex AI Training Job
resource "google_vertex_ai_pipeline" "ml_training" {
  name   = "ml-training-job"
  region = var.GOOGLE_REGION

  training_input {
    scale_tier = "BASIC"
    python_package_uris = ["gs://${var.GOOGLE_BUCKET}/trainer.tar.gz"]
    python_module       = "trainer.task"
    args                = ["--model-dir", "gs://${var.GOOGLE_BUCKET}/models"]
    runtime_version     = "2.11"
    python_version      = "3.11"
  }
}

