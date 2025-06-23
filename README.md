# Dexcom Glucose Analysis

This repository contains a data pipeline and dashboard for processing Dexcom continuous glucose monitoring (CGM) data. It brings together **dbt** for transformations, **Dagster** for orchestration, and **Streamlit** for interactive visualizations.

## Project Overview
- **dbt project** (`dexcom_glucose_analytics`)
  - Cleans and transforms raw glucose readings
  - Produces an analytics-ready mart
- **Dagster project** (`dexcom_dagster`)
  - Ingests new readings from the Dexcom API
  - Triggers dbt models and exports the final parquet file
- **Streamlit dashboard** (`glucose_dashboard`)
  - Loads the latest dataset from S3
  - Displays trend charts and summary statistics

## Repository Layout
```text
├── dexcom_glucose_analytics/   # dbt models, macros, seeds
├── dexcom_dagster/             # Dagster assets, jobs and schedules
├── glucose_dashboard/          # Streamlit application
├── profiles/                   # sample dbt profiles
├── scripts/                    # utility scripts for ingestion & export
└── requirements.txt            # Python dependencies
```

## Getting Started
1. **Clone the repository** and install dependencies
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Configure environment variables** in a `.env` file at the project root
   ```bash
   DEXCOM_USERNAME=your_username
   DEXCOM_PASSWORD=your_password
   DBT_PROFILE_DIR=./profiles
   AWS_S3_BUCKET_NAME=your-bucket
   ```
3. **Run the pipeline locally**
   ```bash
   # Start Dagster webserver
   dagster dev
   # In another terminal, launch the dashboard
   streamlit run glucose_dashboard/app.py
   ```
   Dagster jobs can be triggered from the UI at <http://localhost:3000>.

## Deployment
Scheduled jobs are defined in `.github/workflows/dagster_pipeline.yml`. They ingest data, run dbt models, and export the updated mart to S3 on a daily cadence.

## Requirements
- Python 3.10+
- dbt-core 1.7
- Dagster 1.6
- Streamlit 1.45

## Author
Kyle Jamieson – Data Analyst / Analytics Engineer
