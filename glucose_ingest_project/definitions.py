from dagster import Definitions
from glucose_ingest_project.jobs.pipeline_job import glucose_ingest_job, dbt_job
from glucose_ingest_project.schedules.pipeline_schedule import glucose_ingest_schedule
from glucose_ingest_project.sensors.trigger_dbt_after_ingest import trigger_dbt_after_glucose_ingest


defs = Definitions(
    jobs=[glucose_ingest_job, dbt_job],
    schedules=[glucose_ingest_schedule],
    sensors=[trigger_dbt_after_glucose_ingest],

)


