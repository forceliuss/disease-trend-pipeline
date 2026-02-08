# GCP Public Health & Clinic Trend Tracker

A scalable, serverless data pipeline designed to correlate internal clinic symptom logs with external public health trends (CDC FluView). This platform empowers clinical operations to predict patient surges and optimize resource allocation.

## 🏗️ Architecture

The system follows a modern ELT (Extract, Load, Transform) architecture on Google Cloud Platform:

1.  **Ingestion**: Airflow (Cloud Composer) orchestrates data fetching from the **CDC FluView API** (via CMU Delphi) and internal clinic logs.
2.  **Data Lake**: Raw JSON/CSV files are stored in **Google Cloud Storage (GCS)** for auditability.
3.  **Data Warehouse**: **BigQuery** stores raw data and executes transformations.
4.  **Transformation**: **dbt** (Data Build Tool) cleans, models, and aggregates data into "Marts" for reporting.
5.  **Visualization**: **Metabase** (on Cloud Run) provides interactive dashboards for trend analysis.

> For detailed architecture diagrams and decisions, see [docs/architecture.md](docs/architecture.md).

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:
*   [Python 3.9+](https://www.python.org/downloads/)
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
*   [Terraform](https://developer.hashicorp.com/terraform/install)
*   [Docker](https://docs.docker.com/get-docker/) (optional, for local testing)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/forceliuss/disease-trend-pipeline.git
    cd disease-trend-pipeline
    ```

2.  **Set Up Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Copy the example credentials (or use your own Service Account key from GCP Console):
    ```bash
    # Place your service account key file
    mkdir -p secrets
    cp /path/to/your/key.json secrets/gcp-sa-key.json
    ```
    Create a `.env` file:
    ```bash
    echo "GOOGLE_APPLICATION_CREDENTIALS=./secrets/gcp-sa-key.json" >> .env
    echo "GCP_PROJECT_ID=health-project-486811" >> .env
    ```

### Infrastructure Deployment (Terraform)

Provision the GCP resources (GCS buckets, BigQuery datasets, Cloud Composer/Airflow):

1.  **Initialize Terraform**
    ```bash
    cd terraform
    terraform init
    ```

2.  **Plan and Apply**
    ```bash
    terraform plan -out=tfplan
    terraform apply tfplan
    ```
    > **Note**: This will create billable resources on GCP. Ensure you have the necessary permissions and billing enabled on your project.

## 🛠️ Usage

### Running the Pipeline (Airflow)
Once Cloud Composer is deployed, access the Airflow UI via the URL provided in the Terraform output.
*   **`cdc_ingestion_weekly`**: Triggers every Wednesday to fetch new CDC data.
*   **`clinic_logs_daily`**: Runs daily at 2:00 UTC to ingest internal logs.

### Running Transformations (dbt)
To manually run transformations locally:
```bash
dbt debug  # Test connection
dbt deps   # Install dependencies
dbt run    # Run all models
dbt test   # Run data validation tests
```

## 📂 Project Structure

```
├── dags/                 # Airflow DAGs (Python)
├── dbt_project/          # dbt models, seeds, and tests
├── docs/                 # Documentation (Architecture, Guides, Tickets)
├── scripts/              # Helper scripts (backfills, data generation)
├── terraform/            # Infrastructure as Code (GCP resources)
└── requirements.txt      # Python dependencies
```

---
**Developed by Forceliuss**
