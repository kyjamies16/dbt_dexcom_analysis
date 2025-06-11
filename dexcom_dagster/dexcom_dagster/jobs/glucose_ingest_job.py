# dexcom_dagster/jobs/glucose_ingest_job.py
from dagster import define_asset_job

glucose_ingest_job = define_asset_job(
    name="glucose_ingest_job",
    selection=["ingest_glucose_readings"]
)
