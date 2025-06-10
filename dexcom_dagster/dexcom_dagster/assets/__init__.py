from .ingest_glucose_readings import ingest_glucose_readings
from .dbt_assets import dexcom_glucose_analytics_dbt_assets
from dotenv import load_dotenv
import os

# Explicitly load .env from project root
load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")))

__all__ = ["ingest_glucose_readings", "dexcom_glucose_analytics_dbt_assets"]
