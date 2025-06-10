from dagster import define_asset_job

glucose_then_dbt_job = define_asset_job(
    name="glucose_then_dbt_job",
    selection=["*"]
)
