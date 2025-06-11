from dagster import AssetExecutionContext
from dagster_dbt import dbt_assets, DbtCliResource
from ..constants import dbt_manifest_path

@dbt_assets(manifest=dbt_manifest_path)
def debug_dbt_asset(context: AssetExecutionContext, dbt: DbtCliResource):
    dbt_cli_task = dbt.cli(["build"], context=context)
    yield from dbt_cli_task.stream()
