from dagster import RunRequest, sensor, DefaultSensorStatus
from glucose_ingest_project.jobs.pipeline_job import glucose_ingest_job, dbt_job

@sensor(
    job=dbt_job,
    name="trigger_dbt_after_glucose_ingest",
    minimum_interval_seconds=60,
    default_status=DefaultSensorStatus.RUNNING,
)
def trigger_dbt_after_glucose_ingest(context):
    # Get the most recent successful run of glucose_ingest_job
    recent_runs = context.instance.get_runs(
        job_name=glucose_ingest_job.name,
        limit=1,
        statuses=["SUCCESS"]
    )

    if not recent_runs:
        return None

    latest_run = recent_runs[0]

    # Avoid triggering more than once per run
    if context.last_run_key == latest_run.run_id:
        return None

    # Trigger dbt_job
    return RunRequest(
        run_key=latest_run.run_id,
        run_config={},  # Optional: add runtime config here if needed
    )
