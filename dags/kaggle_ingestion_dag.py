from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago
import os
import sys

sys.path.append(os.path.join(os.environ.get("AIRFLOW_HOME", "/opt/airflow"), "scripts"))

from ingest_kaggle_mental_health import ingest_kaggle_data

# Configuration
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "your-bucket-name")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "your-project-id")
DATASET_ID = "raw_zone"
TABLE_ID = "mental_health"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

with DAG(
    'kaggle_mental_health_ingestion',
    default_args=default_args,
    description='Ingest Mental Health dataset from Kaggle to BigQuery via GCS',
    schedule_interval='@weekly',
    start_date=days_ago(1),
    catchup=False,
    tags=['kaggle', 'ingestion', 'epic2'],
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_to_gcs',
        python_callable=ingest_kaggle_data,
        env={
            "GCS_BUCKET_NAME": GCS_BUCKET_NAME,
            "KAGGLE_USERNAME": os.environ.get("KAGGLE_USERNAME"),
            "KAGGLE_KEY": os.environ.get("KAGGLE_KEY"),
        }
    )
    
    load_to_bq = GCSToBigQueryOperator(
        task_id='gcs_to_bigquery',
        bucket=GCS_BUCKET_NAME,
        source_objects=[f"raw/mental_health/{{{{ ds }}}}/Mental Health Dataset.csv"],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}",
        source_format='CSV',
        write_disposition='WRITE_TRUNCATE',
        autodetect=True,
        skip_leading_rows=1,
    )

    ingest_task >> load_to_bq
