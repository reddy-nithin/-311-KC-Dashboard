import pandas as pd
import time
import os
from sodapy import Socrata
from google.oauth2 import service_account
from pandas_gbq import read_gbq

# --- CONFIGURATION ---
PROJECT_ID = 'kc-311-pipeline' # <--- VERIFY THIS IS CORRECT
dataset_id = '311_data'
table_id = 'service_requests'
full_table_path = f"{dataset_id}.{table_id}"
key_path = 'gbq_key.json' # GitHub will create this file for us

# --- AUTHENTICATION ---
# We check if the key file exists (created by GitHub Actions)
if os.path.exists(key_path):
    credentials = service_account.Credentials.from_service_account_file(key_path)
else:
    raise FileNotFoundError("gbq_key.json not found! Check GitHub Secrets.")

# --- STEP 1: CHECK BIGQUERY ---
print("Checking BigQuery for latest data...")
try:
    query = f"SELECT MAX(last_updated_ymd) as max_date FROM `{PROJECT_ID}.{full_table_path}`"
    max_date_df = read_gbq(query, project_id=PROJECT_ID, credentials=credentials)
    print(f"Status: Found existing data. Last update: {max_date_df['max_date'].iloc[0]}")
except:
    print("Status: Table likely doesn't exist. Proceeding with full load.")

# --- STEP 2: INGEST (100k Rows) ---
print("\nFetching data from KC Socrata API...")
client = Socrata("data.kcmo.org", None)
# We pull 100k to ensure we get your old history + new data
results = client.get("d4px-6rwg", limit=100000, order='last_updated DESC')
df = pd.DataFrame.from_records(results)
print(f"Fetched {len(df)} rows.")

# --- STEP 3: TRANSFORMATION ---
print("\nTransforming data...")

# Drop Cols
cols_to_drop = ['workorder_', 'incident_address', 'lat_long', 'additional_questions']
df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors='ignore')

# Rename
if 'reported_issue' in df.columns:
    df.rename(columns={'reported_issue': 'issue_id'}, inplace=True)

# Date Splitting
def split_date_time(df, source_col, ymd_col, hms_col):
    if source_col in df.columns:
        df[source_col] = pd.to_datetime(df[source_col], errors='coerce')
        df[ymd_col] = df[source_col].dt.strftime('%Y-%m-%d')
        df[hms_col] = df[source_col].dt.strftime('%H:%M:%S')
        df.drop(columns=[source_col], inplace=True)

split_date_time(df, 'last_updated', 'last_updated_ymd', 'last_updated_hms')
split_date_time(df, 'resolved_date', 'resolved_date_ymd', 'resolved_date_hms')
split_date_time(df, 'open_date_time', 'open_date_time_ymd', 'open_date_time_hms')

# Lowercase Status
if 'current_status' in df.columns:
    df['current_status'] = df['current_status'].str.lower()

# Timestamp
df['ingest_timestamp'] = int(time.time())

# --- STEP 4: DEDUPLICATION ---
try:
    existing_ids = read_gbq(f"SELECT issue_id FROM `{PROJECT_ID}.{full_table_path}`", project_id=PROJECT_ID, credentials=credentials)
    if not existing_ids.empty:
        existing_id_set = set(existing_ids['issue_id'])
        initial_count = len(df)
        df = df[~df['issue_id'].isin(existing_id_set)]
        print(f"Deduplication: Filtered out {initial_count - len(df)} duplicate rows.")
except:
    print("Deduplication: Skipping (First run or table empty).")

# --- STEP 5: LOAD ---
if not df.empty:
    print(f"\nUploading {len(df)} NEW records to BigQuery...")
    df.to_gbq(destination_table=full_table_path,
              project_id=PROJECT_ID,
              credentials=credentials,
              if_exists='append')
    print("SUCCESS: Data pipeline finished!")
else:
    print("\nSUCCESS: No new unique data to upload.")
