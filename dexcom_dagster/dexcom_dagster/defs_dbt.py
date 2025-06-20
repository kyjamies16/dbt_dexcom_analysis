from dagster import Definitions
from dagster_dbt import DbtCliResource

from .dbt_constants import (
    DBT_PROJECT_PATH,
    DBT_TARGET,
    DBT_PROFILES_DIR
)

from .assets.dbt_assets import all_dbt_assets
from .assets.export_mart_to_parquet_and_upload import export_glucose_to_parquet_and_upload

from .jobs.export_job import export_job
from .jobs.dbt_pipeline_job import partitioned_dbt_job

from .schedules.schedules import schedules


dbt = DbtCliResource(
    project_dir=str(DBT_PROJECT_PATH),
    profiles_dir=str(DBT_PROFILES_DIR),
    target=DBT_TARGET,
    working_directory=str(DBT_PROJECT_PATH),
    global_config_flags=["--debug"],
)


defs_dbt = Definitions(
    assets=[
        all_dbt_assets,                         
        export_glucose_to_parquet_and_upload,   
    ],
    jobs=[
        partitioned_dbt_job,   
        export_job,            
    ],
    schedules=schedules,
    resources={
        "dbt": dbt,
    },
)
