"""
KC 311 Service Request Data Pipeline

This script implements an automated ETL pipeline that:
1. Fetches data from Kansas City's Open Data API (Socrata)
2. Transforms and cleans the data
3. Deduplicates against existing records
4. Loads new records into Google BigQuery

Author: Nithin Reddy
Course: Big Data Management
"""

import pandas as pd
import time
import os
from sodapy import Socrata
from google.oauth2 import service_account
from pandas_gbq import read_gbq

# Import configuration
from config import (
    GCP_PROJECT_ID,
    FULL_TABLE_PATH,
    GCP_KEY_PATH,
    SOCRATA_DOMAIN,
    SOCRATA_DATASET_ID,
    FETCH_LIMIT
)


def get_credentials():
    """Authenticate with Google Cloud using service account."""
    if os.path.exists(GCP_KEY_PATH):
        return service_account.Credentials.from_service_account_file(GCP_KEY_PATH)
    raise FileNotFoundError(f"{GCP_KEY_PATH} not found! Check GitHub Secrets.")


def get_latest_update_date(credentials):
    """Check BigQuery for the most recent data update."""
    print("Checking BigQuery for latest data...")
    try:
        query = f"SELECT MAX(last_updated_ymd) as max_date FROM `{GCP_PROJECT_ID}.{FULL_TABLE_PATH}`"
        max_date_df = read_gbq(query, project_id=GCP_PROJECT_ID, credentials=credentials)
        print(f"Status: Found existing data. Last update: {max_date_df['max_date'].iloc[0]}")
        return max_date_df['max_date'].iloc[0]
    except Exception:
        print("Status: Table likely doesn't exist. Proceeding with full load.")
        return None


def fetch_data():
    """Fetch data from Kansas City Socrata API."""
    print("\nFetching data from KC Socrata API...")
    client = Socrata(SOCRATA_DOMAIN, None)
    results = client.get(SOCRATA_DATASET_ID, limit=FETCH_LIMIT, order='last_updated DESC')
    df = pd.DataFrame.from_records(results)
    print(f"Fetched {len(df)} rows.")
    return df


def transform_data(df):
    """Apply transformations to the dataframe."""
    print("\nTransforming data...")
    
    # Drop unnecessary columns
    cols_to_drop = ['workorder_', 'incident_address', 'lat_long', 'additional_questions']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors='ignore')
    
    # Rename columns
    if 'reported_issue' in df.columns:
        df.rename(columns={'reported_issue': 'issue_id'}, inplace=True)
    
    # Split datetime columns
    def split_date_time(df, source_col, ymd_col, hms_col):
        if source_col in df.columns:
            df[source_col] = pd.to_datetime(df[source_col], errors='coerce')
            df[ymd_col] = df[source_col].dt.strftime('%Y-%m-%d')
            df[hms_col] = df[source_col].dt.strftime('%H:%M:%S')
            df.drop(columns=[source_col], inplace=True)
    
    split_date_time(df, 'last_updated', 'last_updated_ymd', 'last_updated_hms')
    split_date_time(df, 'resolved_date', 'resolved_date_ymd', 'resolved_date_hms')
    split_date_time(df, 'open_date_time', 'open_date_time_ymd', 'open_date_time_hms')
    
    # Normalize status values
    if 'current_status' in df.columns:
        df['current_status'] = df['current_status'].str.lower()
    
    # Add ingestion timestamp
    df['ingest_timestamp'] = int(time.time())
    
    return df


def deduplicate_data(df, credentials):
    """Remove records that already exist in BigQuery."""
    try:
        existing_ids = read_gbq(
            f"SELECT issue_id FROM `{GCP_PROJECT_ID}.{FULL_TABLE_PATH}`",
            project_id=GCP_PROJECT_ID,
            credentials=credentials
        )
        if not existing_ids.empty:
            existing_id_set = set(existing_ids['issue_id'])
            initial_count = len(df)
            df = df[~df['issue_id'].isin(existing_id_set)]
            print(f"Deduplication: Filtered out {initial_count - len(df)} duplicate rows.")
    except Exception:
        print("Deduplication: Skipping (First run or table empty).")
    return df


def load_data(df, credentials):
    """Upload new records to BigQuery."""
    if not df.empty:
        print(f"\nUploading {len(df)} NEW records to BigQuery...")
        df.to_gbq(
            destination_table=FULL_TABLE_PATH,
            project_id=GCP_PROJECT_ID,
            credentials=credentials,
            if_exists='append'
        )
        print("SUCCESS: Data pipeline finished!")
    else:
        print("\nSUCCESS: No new unique data to upload.")


def main():
    """Main pipeline execution."""
    credentials = get_credentials()
    get_latest_update_date(credentials)
    
    df = fetch_data()
    df = transform_data(df)
    df = deduplicate_data(df, credentials)
    load_data(df, credentials)


if __name__ == "__main__":
    main()
