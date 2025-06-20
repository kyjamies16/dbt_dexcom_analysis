# dbt_constants.py
import os
from pathlib import Path
from .core_constants import REPO_ROOT

DBT_PROJECT_PATH = REPO_ROOT / os.getenv("DBT_PROJECT_PATH", "dexcom_glucose_analytics")
DBT_PROFILES_DIR = REPO_ROOT / os.getenv("DBT_PROFILES_DIR", "profiles")
DBT_TARGET = os.getenv("DBT_TARGET", "prod")

dbt_manifest_path = DBT_PROJECT_PATH / "target" / "manifest.json"
