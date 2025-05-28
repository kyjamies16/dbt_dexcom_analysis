from dagster import ScheduleDefinition
from glucose_ingest_project.jobs.pipeline_job import glucose_ingest_job, dbt_job

glucose_ingest_schedule = ScheduleDefinition(
    job=glucose_ingest_job,
    cron_schedule="*/5 * * * *",  # every 5 minutes
)

dbt_schedule = ScheduleDefinition(
    job=dbt_job,
    cron_schedule="0 6 * * *",  # every day at 6am
)