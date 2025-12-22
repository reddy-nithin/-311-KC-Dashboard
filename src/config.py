"""
Configuration module for KC 311 Data Pipeline.

Loads environment variables from .env file (local development) 
or environment (GitHub Actions).
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# ============================================
# Google Cloud / BigQuery Configuration
# ============================================
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'kc-311-pipeline')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', '311_data')
BIGQUERY_TABLE = os.getenv('BIGQUERY_TABLE', 'service_requests')
GCP_KEY_PATH = os.getenv('GCP_KEY_PATH', 'gbq_key.json')

# Derived configuration
FULL_TABLE_PATH = f"{BIGQUERY_DATASET}.{BIGQUERY_TABLE}"

# ============================================
# API Configuration
# ============================================
SOCRATA_DOMAIN = 'data.kcmo.org'
SOCRATA_DATASET_ID = 'd4px-6rwg'
FETCH_LIMIT = 20000
