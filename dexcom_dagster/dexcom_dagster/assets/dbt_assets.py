from dagster import AssetExecutionContext
from dagster_dbt import dbt_assets, DbtCliResource
from pathlib import Path

manifest_path = Path("C:/Users/krjam/dexcom/dexcom_glucose_analytics/target/manifest.json")

@dbt_assets(
    manifest=manifest_path,
    exclude= "int_glucose_readings_combined mart_glucose_readings"
)
def dexcom_glucose_analytics_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

