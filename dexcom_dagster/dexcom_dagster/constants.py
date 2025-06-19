import os
from pathlib import Path
from .utils.env import load_environment


# Load environment (.env.dev or .env.prod)
load_environment()

# DBT project configuration
DBT_PROJECT_PATH = Path(os.getenv("DBT_PROJECT_PATH", "C:/Users/krjam/dexcom/dexcom_glucose_analytics"))
DBT_PROFILES_DIR = os.getenv("DBT_PROFILE_DIR", "C:/Users/krjam/.dbt")
DBT_TARGET = os.getenv("DBT_TARGET", "prod")
DB_PATH = os.getenv("DATABASE_PATH", "C:/Users/krjam/dexcom/dbt_duckdb_prod.db")
dbt_manifest_path = DBT_PROJECT_PATH / "target" / "manifest.json"




