from dagster import job
from glucose_ingest_project.ops.run_script import run_glucose_script
from glucose_ingest_project.ops.run_dbt import run_dbt

@job
def glucose_ingest_job():
    run_glucose_script()

@job
def dbt_job():
    run_dbt()
