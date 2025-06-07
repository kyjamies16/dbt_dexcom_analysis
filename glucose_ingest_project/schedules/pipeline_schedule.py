from dagster import ScheduleDefinition
from glucose_ingest_project.jobs.pipeline_job import glucose_ingest_job

glucose_ingest_schedule = ScheduleDefinition(
    job=glucose_ingest_job,
    cron_schedule="30 9 * * *",  # Runs every day at 9:30 AM
)

