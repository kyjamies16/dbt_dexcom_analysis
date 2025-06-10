import os
from dagster import Definitions
from dagster_dbt import DbtCliResource

from .assets.dbt_assets import dexcom_glucose_analytics_dbt_assets
from .assets.ingest_glucose_readings import ingest_glucose_readings
from .jobs.glucose_then_dbt_job import glucose_then_dbt_job
from .schedules.schedules import schedules

# Set env var for dbt log location
os.environ["DBT_LOG_PATH"] = "C:/Users/krjam/dexcom/dexcom_glucose_analytics/logs/dbt.log"

defs = Definitions(
    assets=[
        dexcom_glucose_analytics_dbt_assets,
        ingest_glucose_readings,
    ],
    jobs=[glucose_then_dbt_job],
    schedules=schedules,
    resources={
        "dbt": DbtCliResource(
            project_dir="C:/Users/krjam/dexcom/dexcom_glucose_analytics",
            profiles_dir="C:/Users/krjam/.dbt",
        ),
    },
)
