# Dexcom Glucose Data Pipeline and Dashboard

## 📈 Overview

This project is a **full-stack data pipeline and analytics dashboard** for managing and visualizing **Dexcom blood glucose data**. It combines:

* **dbt** for data modeling, transformation, and testing
* **Dagster** for orchestration and scheduling
* **Streamlit** for an interactive web app and dashboards

The pipeline ingests raw data from Dexcom APIs (and/or t\:connect CSV exports), processes it into analytics-ready tables, and serves visual insights via a user-friendly dashboard.

---

## 🗂️ Project Structure

```
root/
│
├── dexcom_glucose_analytics/   # dbt project
│   ├── models/
│   ├── macros/
│   ├── seeds/
│   ├── dbt_project.yml
│   └── profiles.yml (local or ~/.dbt/profiles.yml)
│
├── dexcom_dagster/             # Dagster project
│   ├── assets/
│   ├── jobs/
│   ├── schedules/
│   ├── definitions.py
│   └── ...
│
├── glucose_dashboard/          # Streamlit app
│   ├── app.py
│   ├── utils/
│   └── ...
│
├── .env                        # environment variables (excluded from repo)
├── requirements.txt            # Python dependencies
└── README.md                   # You are here!
```

---

## ⚙️ How It Works

### 1️⃣ **dbt**

* **Purpose:** Cleans, transforms, and tests raw glucose data.
* **Key models:**

  * `stg_pydex_readings`: raw ingested readings.
  * `int_glucose_readings`: intermediate cleansed version.
  * `mart_glucose_readings`: final analytics-ready mart.
* **Run:**

  ```bash
  dbt run
  dbt test
  ```

---

### 2️⃣ **Dagster**

* **Purpose:** Orchestrates data ingestion from Dexcom APIs, runs dbt models, and schedules pipeline jobs.
* **Key jobs:**

  * `glucose_ingest_job`: Ingests new glucose readings.
  * `materialize_dbt_job`: Runs dbt transformations.
* **Run locally:**

  ```bash
  dagster dev
  ```

  Open Dagster UI at [http://localhost:3000](http://localhost:3000) to trigger jobs or view logs.

---

### 3️⃣ **Streamlit**

* **Purpose:** Interactive web dashboard to explore glucose trends, patterns, and anomalies.

* **Run locally:**

  ```bash
  streamlit run glucose_dashboard/app.py
  ```

* **Deploy:**

  * Connect your repo to [Streamlit Cloud](https://streamlit.io/cloud).
  * Set the app path to `glucose_dashboard/app.py`.
  * Add required secrets (.env vars) in Streamlit Cloud settings.

---

## ✅ Setup Instructions

### 🔑 1. Clone & Install

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

---

### 🔐 2. Configure Environment Variables

Create a `.env` file at the project root:

```bash
DEXCOM_USERNAME=your_username
DEXCOM_PASSWORD=your_password
DATABASE_PATH=path/to/your/duckdb.db
DBT_PROFILE_DIR=path/to/.dbt
DAGSTER_HOME=path/to/dagster_home
```

Add `.env` to `.gitignore`!

---

### ⚡ 3. Run the Pipeline

* **Ingest new data:**

  ```bash
  dagster dev
  # or trigger ingest job from Dagster UI
  ```

* **Transform data:**

  ```bash
  dbt run
  ```

* **Launch dashboard:**

  ```bash
  streamlit run glucose_dashboard/app.py
  ```

---

## 📅 Deployment

* **Dagster:** can be deployed using Dagster Cloud or a server.
* **Streamlit:** can be deployed with Streamlit Cloud (recommended for quick demos).

---

## 🧰 Requirements

* Python >= 3.10
* dbt-core >= 1.7
* Dagster >= 1.7
* Streamlit >= 1.30
* DuckDB (used as local warehouse)

---

## 🗝️ Secrets

Make sure to store secrets like Dexcom credentials securely. Use `.env` locally and Streamlit/Dagster Cloud secrets in production.

---

## 🧑‍💻 Author

**Your Name**
Data Analyst / Analytics Engineer
[LinkedIn](#) | [GitHub](#)

---

## ✅ TODO

*

---

## 📄 License

Specify your license here (e.g., MIT).

---

## 🚀 Quick Start

```bash
# One-liner for dev:
dagster dev & streamlit run glucose_dashboard/app.py
```

---

##
