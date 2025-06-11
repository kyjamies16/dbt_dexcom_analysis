from dagster import define_asset_job

materialize_dbt_job = define_asset_job(
    name="materialize_dbt_job",
    selection=["*"]
,
)
