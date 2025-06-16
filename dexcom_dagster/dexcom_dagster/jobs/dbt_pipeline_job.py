
from dagster import define_asset_job
from ..assets.dbt_assets import all_dbt_assets

partitioned_dbt_job = define_asset_job(
    name="dbt_pipeline_job",
    selection=[all_dbt_assets],
)
