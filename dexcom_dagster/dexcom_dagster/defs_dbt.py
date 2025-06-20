from dagster import Definitions
from dagster_dbt import DbtCliResource

from .constants import (
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
        all_dbt_assets,                         # the dbt manifest models
        export_glucose_to_parquet_and_upload,   # the export mart step depends on dbt mart
    ],
    jobs=[
        partitioned_dbt_job,   # your main dbt pipeline job
        export_job,            # upload to S3: works on the mart → needs dbt pipeline to run first
    ],
    schedules=schedules,
    resources={
        "dbt": dbt,
    },
)
