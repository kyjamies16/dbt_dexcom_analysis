from dagster import ScheduleDefinition
from ..jobs.glucose_then_dbt_job import glucose_then_dbt_job

schedules = [
    ScheduleDefinition(
        job=glucose_then_dbt_job,
        cron_schedule="30 9 * * *",  # 9:30 AM
        execution_timezone="US/Central",
        name="daily_glucose_dbt_run",
    )
]
