import os
from pathlib import Path
from dotenv import load_dotenv


# Absolute path: go UP from THIS file to the repo root
dotenv_path = Path(__file__).resolve().parents[2] / ".env.prod"

# Try loading .env.dev or .env
env_loaded = load_dotenv(dotenv_path) or load_dotenv(".env")

if not env_loaded:
    print("⚠️  Warning: No .env.prod or .env found — make sure you have proper environment variables set.")

# --- CONFIG ---
# DBT project config
DBT_PROJECT_PATH = Path(os.getenv("DBT_PROJECT_PATH", "C:/Users/krjam/dexcom/dexcom_glucose_analytics"))
DBT_PROFILES_DIR = os.getenv("DBT_PROFILE_DIR", "C:/Users/krjam/.dbt")
DBT_TARGET = os.getenv("DBT_TARGET", "prod")

# Local DuckDB fallback for dev
DB_PATH = os.getenv("DATABASE_PATH", "C:/Users/krjam/dexcom/dbt_duckdb_prod.db")

# DBT manifest path
dbt_manifest_path = DBT_PROJECT_PATH / "target" / "manifest.json"
