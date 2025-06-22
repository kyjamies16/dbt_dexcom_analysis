from dagster import define_asset_job

export_job = define_asset_job(
    name="export_job",
    selection=["export_glucose_to_parquet_and_upload"]
)
