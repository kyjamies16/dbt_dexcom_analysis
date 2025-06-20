# core_constants.py
import os
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]

dotenv_path = REPO_ROOT / ".env.prod"
env_loaded = load_dotenv(dotenv_path) or load_dotenv(REPO_ROOT / ".env")

if not env_loaded:
    print(f"⚠️  Warning: No .env.prod or .env found in {REPO_ROOT} — using system env vars.")

# ✅ Pure core config
DB_PATH = REPO_ROOT / os.getenv("DATABASE_PATH", "dbt_duckdb_prod.db")
