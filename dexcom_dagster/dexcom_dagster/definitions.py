# definitions.py
from dagster import Definitions
from dagster_dbt import DbtCliResource

from .constants import (
    DBT_PROJECT_PATH,
    DBT_PROFILES_DIR,
    DBT_TARGET,
) 

from .assets.ingest_glucose_readings import ingest_glucose_readings
from .assets.dbt_assets import all_dbt_assets
from .assets.export_mart_to_parquet_and_upload import export_glucose_to_parquet_and_upload

from .jobs.export_job import export_job
from .jobs.glucose_ingest_job import glucose_ingest_job
from .jobs.dbt_pipeline_job import partitioned_dbt_job

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
    assets=[all_dbt_assets,ingest_glucose_readings,export_glucose_to_parquet_and_upload],
    jobs=[glucose_ingest_job, partitioned_dbt_job, export_job],
    schedules=schedules,
    resources={
        "dbt": dbt,  
    },
)
