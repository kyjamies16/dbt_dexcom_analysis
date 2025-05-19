from dagster import Definitions
from glucose_ingest_project.assets import ingest_glucose_reading
from glucose_ingest_project.jobs import ingest_glucose_job
from glucose_ingest_project.schedules import glucose_ingest_schedule

defs = Definitions(
    assets=[ingest_glucose_reading],
    jobs=[ingest_glucose_job],
    schedules=[glucose_ingest_schedule],
)
