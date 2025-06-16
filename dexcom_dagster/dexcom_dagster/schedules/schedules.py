# schedules/schedules.py

from dagster import ScheduleDefinition, build_schedule_from_partitioned_job
from ..jobs.glucose_ingest_job import glucose_ingest_job
from ..jobs.dbt_pipeline_job import partitioned_dbt_job

schedules = [
    # Ingestion job: plain schedule
    ScheduleDefinition(
        job=glucose_ingest_job,
        cron_schedule="25 9 * * *",
        execution_timezone="US/Central",
        name="daily_glucose_ingest_run",
    ),

    # DBT pipeline job: proper partitioned schedule helper
    build_schedule_from_partitioned_job(
        job=partitioned_dbt_job,
        minute_of_hour=30,
        hour_of_day=9,
    ),
]
