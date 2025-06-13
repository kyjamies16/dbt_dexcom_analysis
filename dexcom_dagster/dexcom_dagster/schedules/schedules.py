# dexcom_dagster/schedules/schedules.py
from dagster import ScheduleDefinition
from ..jobs.glucose_ingest_job import glucose_ingest_job
from ..assets import debug_dbt_asset
from dagster_dbt import build_schedule_from_dbt_selection

schedules = [
  ScheduleDefinition(
    job=glucose_ingest_job,
    cron_schedule="25 9 * * *",  # 9:25 AM
    execution_timezone="US/Central",
    name="daily_glucose_ingest_run",
  ),
  build_schedule_from_dbt_selection(
    [debug_dbt_asset],
    job_name="materialize_dbt_models",
    cron_schedule="30 9 * * *",
    execution_timezone="US/Central",
    dbt_select="fqn:*",
  ),
]
