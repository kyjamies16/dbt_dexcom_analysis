# definitions.py
from dagster import Definitions
from dagster_dbt import DbtCliResource

from .constants import (
    DBT_PROJECT_PATH,
    DBT_PROFILES_DIR,
    DBT_TARGET,
) 

from .assets.ingest_glucose_readings import ingest_glucose_readings
from .assets.dbt_assets import debug_dbt_asset, int_glucose_readings_combined_asset
from .assets.dbt_assets import int_glucose_readings_combined_asset

from .jobs.glucose_ingest_job import glucose_ingest_job
from .schedules.schedules import schedules

# Dagster resource used in definitions.py
dbt = DbtCliResource(
    project_dir=str(DBT_PROJECT_PATH),
    profiles_dir=DBT_PROFILES_DIR,
    target=DBT_TARGET,
    working_directory=str(DBT_PROJECT_PATH),
    global_config_flags=["--debug"],
)


defs = Definitions(
    assets=[
        debug_dbt_asset,
        int_glucose_readings_combined_asset,
        ingest_glucose_readings,
    ],
    jobs=[
        glucose_ingest_job,
    ],
    schedules=schedules,
    resources={
        "dbt": dbt,  
    },
)
