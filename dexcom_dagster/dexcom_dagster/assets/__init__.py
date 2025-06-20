import os
from dotenv import load_dotenv

# Load .env from project root
dotenv_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".env")
)
load_dotenv(dotenv_path=dotenv_path)

# ✅ Only pure Python assets — no dbt!
from .ingest_glucose_readings import ingest_glucose_readings

__all__ = [
    "ingest_glucose_readings",
]
