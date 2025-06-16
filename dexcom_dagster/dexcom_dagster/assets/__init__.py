# dexcom_dagster/assets/__init__.py

import os
from dotenv import load_dotenv

# 1) Load your .env from the project root (two levels up from assets/)
dotenv_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".env")
)
load_dotenv(dotenv_path=dotenv_path)

# 2) Export the assets in this package
from .ingest_glucose_readings import ingest_glucose_readings
from .dbt_assets import all_dbt_assets

__all__ = [
    "ingest_glucose_readings",
    "all_dbt_assets",
]
