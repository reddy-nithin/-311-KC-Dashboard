# 🏙️ Kansas City 311 Insight Engine

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![BigQuery](https://img.shields.io/badge/Google-BigQuery-4285F4.svg)](https://cloud.google.com/bigquery)
[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF.svg)](https://github.com/features/actions)
[![Tableau](https://img.shields.io/badge/Tableau-Public-E97627.svg)](https://public.tableau.com/)

> **Academic Project** | Big Data Management Course  
> An automated data pipeline for analyzing Kansas City 311 service requests

---

## 📋 Overview

This project implements an end-to-end data engineering pipeline that extracts, transforms, and loads (ETL) civic service request data from Kansas City's Open Data Portal into a cloud data warehouse for analysis and visualization.

**Key Objectives:**
- Demonstrate proficiency in cloud-based data engineering
- Automate data ingestion using CI/CD practices
- Enable real-time municipal service analytics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KC 311 DATA PIPELINE ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│   │   KC Open    │      │   Python/    │      │   Google     │              │
│   │   Data API   │ ───▶ │   Pandas     │ ───▶ │   BigQuery   │              │
│   │   (Socrata)  │      │   ETL        │      │   (DWH)      │              │
│   └──────────────┘      └──────────────┘      └──────────────┘              │
│                               │                      │                       │
│                               │                      │                       │
│                               ▼                      ▼                       │
│                        ┌──────────────┐      ┌──────────────┐               │
│                        │   GitHub     │      │   Tableau    │               │
│                        │   Actions    │      │   Public     │               │
│                        │   (Scheduler)│      │   (Viz)      │               │
│                        └──────────────┘      └──────────────┘               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

> 📸 **Architecture Diagram**: Place a visual diagram screenshot in `docs/architecture.png`

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🔄 Automated Ingestion** | GitHub Actions runs the pipeline on a configurable schedule (weekly by default) |
| **🧹 Data Quality** | Automated deduplication prevents duplicate records |
| **☁️ Cloud-Native** | Leverages Google BigQuery for scalable analytics |
| **📊 Visual Analytics** | Interactive Tableau dashboard for insights |
| **🔐 Secure Credentials** | GCP service account keys managed via GitHub Secrets |

---

## 📊 Dashboard

<!-- TODO: Add your Tableau dashboard screenshot -->
> 📸 **Dashboard Preview**: Place your dashboard screenshot in `docs/dashboard_preview.png`

![Dashboard Preview](docs/dashboard_preview.png)

**🔗 [View Live Dashboard on Tableau Public](https://public.tableau.com/views/YOUR_DASHBOARD_LINK)**

*Replace the link above with your actual Tableau Public URL*

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Data Source** | [Kansas City Open Data](https://data.kcmo.org/) (Socrata API) |
| **Processing** | Python 3.9+, Pandas |
| **Data Warehouse** | Google BigQuery |
| **Orchestration** | GitHub Actions |
| **Visualization** | Tableau Public |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account with BigQuery enabled
- GCP Service Account with BigQuery permissions

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/311-KC-Dashboard.git
   cd 311-KC-Dashboard
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your GCP project details
   ```

5. **Add your GCP credentials**
   - Download your service account JSON key from GCP Console
   - Save it as `gbq_key.json` in the project root
   - ⚠️ Never commit this file (it's in `.gitignore`)

### Running Locally

```bash
cd src
python pipeline.py
```

---

## 📁 Project Structure

```
311-KC-Dashboard/
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
│
├── src/                    # Source code
│   ├── __init__.py
│   ├── config.py           # Configuration loader
│   └── pipeline.py         # Main ETL script
│
├── docs/                   # Documentation & visuals
│   ├── architecture.png    # Architecture diagram
│   └── dashboard_preview.png
│
└── .github/
    └── workflows/
        └── hourly_scheduler.yml  # GitHub Actions workflow
```

---

## ⚙️ GitHub Actions Configuration

The pipeline runs automatically via GitHub Actions. To configure:

1. **Add Repository Secret**
   - Go to: Settings → Secrets → Actions
   - Add secret named `GCP_SA_KEY` containing your service account JSON

2. **Adjust Schedule** (optional)
   - Edit `.github/workflows/hourly_scheduler.yml`
   - Modify the cron expression as needed

---

## 📈 Data Schema

| Column | Type | Description |
|--------|------|-------------|
| `issue_id` | STRING | Unique identifier for each request |
| `current_status` | STRING | Status (open, closed, etc.) |
| `category` | STRING | Service category |
| `open_date_time_ymd` | DATE | Request creation date |
| `resolved_date_ymd` | DATE | Resolution date (if applicable) |
| `ingest_timestamp` | INTEGER | Pipeline run timestamp |

---

## 👨‍💻 Author

**Nithin Reddy**  
Graduate Student | Data Engineering  
*Big Data Management Course Project*

---

## 📄 License

This project is for educational purposes as part of academic coursework.
