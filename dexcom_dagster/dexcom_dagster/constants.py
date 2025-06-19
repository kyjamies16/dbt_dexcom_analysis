import os
from pathlib import Path
from dotenv import load_dotenv

# -------------
# Always resolve paths relative to REPO_ROOT
# -------------
REPO_ROOT = Path(__file__).resolve().parents[2]

# Load .env.prod first, fallback to .env
dotenv_path = REPO_ROOT / ".env.prod"
env_loaded = load_dotenv(dotenv_path) or load_dotenv(REPO_ROOT / ".env")

if not env_loaded:
    print(f"⚠️  Warning: No .env.prod or .env found in {REPO_ROOT} — using system env vars.")

# -------------

# 💡 ALWAYS RESOLVE PATHS AGAINST REPO_ROOT
DBT_PROJECT_PATH = REPO_ROOT / os.getenv("DBT_PROJECT_PATH", "dexcom_glucose_analytics")
DBT_PROFILES_DIR = REPO_ROOT / os.getenv("DBT_PROFILES_DIR", "profiles")
DBT_TARGET = os.getenv("DBT_TARGET", "prod")
DB_PATH = REPO_ROOT / os.getenv("DATABASE_PATH", "dbt_duckdb_prod.db")

dbt_manifest_path = DBT_PROJECT_PATH / "target" / "manifest.json"

