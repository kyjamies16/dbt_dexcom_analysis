from dagster import ScheduleDefinition
from .jobs import ingest_glucose_job

glucose_ingest_schedule = ScheduleDefinition(
    job=ingest_glucose_job,
    cron_schedule="*/5 * * * *",  # ✅ every 5 minutes
    execution_timezone="US/Central"
)
