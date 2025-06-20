from dagster import Definitions

from .assets.ingest_glucose_readings import ingest_glucose_readings
from .jobs.glucose_ingest_job import glucose_ingest_job

defs_ingest = Definitions(
    assets=[ingest_glucose_readings],
    jobs=[glucose_ingest_job],
)
