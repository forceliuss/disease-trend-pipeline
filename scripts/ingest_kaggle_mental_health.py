import os
import datetime
import shutil
import kagglehub
import pandas as pd
from google.cloud import storage

# Configuration
DATASET_NAME = "imtkaggleteam/mental-health"
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "your-bucket-name-here") # Replace with actual bucket name or env var
GCS_PATH_PREFIX = "raw/mental_health"

def ingest_kaggle_data():
    """
    Downloads the dataset from Kaggle, saves it locally as CSV,
    and uploads it to GCS.
    """
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    print(f"[{date_str}] Starting ingestion for {DATASET_NAME}...")

    # 1. Download from Kaggle
    try:
        # kagglehub downloads to a local cache directory
        path = kagglehub.dataset_download(DATASET_NAME)
        print(f"Dataset downloaded to: {path}")
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        raise

    # 2. Find the CSV file(s)
    # The dataset might contain multiple files. We'll look for CSVs.
    csv_files = [f for f in os.listdir(path) if f.endswith('.csv')]
    
    if not csv_files:
        raise FileNotFoundError("No CSV files found in the downloaded dataset.")

    print(f"Found CSV files: {csv_files}")

    # 3. Upload to GCS
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    for csv_file in csv_files:
        local_file_path = os.path.join(path, csv_file)
        
        # Read into Pandas to verify/clean if needed (optional for now, just direct upload is strictly safer for raw)
        # But per requirements, let's just upload raw file.
        # We'll stick to uploading the raw file to GCS to maintain ELT pattern.
        
        blob_name = f"{GCS_PATH_PREFIX}/{date_str}/{csv_file}"
        blob = bucket.blob(blob_name)
        
        print(f"Uploading {local_file_path} to gs://{GCS_BUCKET_NAME}/{blob_name}...")
        blob.upload_from_filename(local_file_path)
        print("Upload complete.")

    print("Ingestion finished successfully.")

if __name__ == "__main__":
    # Check for GCS bucket env var
    if not os.environ.get("GCS_BUCKET_NAME"):
         print("WARNING: GCS_BUCKET_NAME environment variable not set. Upload may fail if bucket doesn't exist.")
    
    ingest_kaggle_data()
