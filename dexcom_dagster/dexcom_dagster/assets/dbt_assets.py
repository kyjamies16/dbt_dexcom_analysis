# dexcom_dagster/assets/dbt_assets_combined.py

import json
from typing import Any, Mapping

from dagster import AssetExecutionContext, DailyPartitionsDefinition
from dagster_dbt import (
  dbt_assets,
  DbtCliResource,
  DagsterDbtTranslator,
  default_metadata_from_dbt_resource_props,
)
from ..constants import dbt_manifest_path
from ..resources.dagster_dbt_translator import CustomDagsterDbtTranslator

# ---------- Non-Partitioned Assets ----------
@dbt_assets(
  manifest=dbt_manifest_path,
  exclude="int_glucose_readings_combined",  # exclude partitioned model
  dagster_dbt_translator=CustomDagsterDbtTranslator(),
  
)
def debug_dbt_asset(context: AssetExecutionContext, dbt: DbtCliResource):
  """Runs all dbt models except the partitioned incremental one."""
  yield from dbt.cli(["build"], context=context).stream()

# ---------- Partitioned Asset ----------
# Daily partitions from the start of live data collection
daily_partitions = DailyPartitionsDefinition(start_date="2025-05-19")

# Custom translator to attach partition_expr to the asset
class PartitionAwareDbtTranslator(DagsterDbtTranslator):
  def get_metadata(self, dbt_resource_props: Mapping[str, Any]) -> Mapping[str, Any]:
    metadata = {"partition_expr": "reading_date"}
    default_metadata = default_metadata_from_dbt_resource_props(dbt_resource_props)
    return {**default_metadata, **metadata}

@dbt_assets(
  manifest=dbt_manifest_path,
  select="int_glucose_readings_combined",  # partitioned model only
  partitions_def=daily_partitions,
  dagster_dbt_translator=PartitionAwareDbtTranslator(),
  
)
def int_glucose_readings_combined_asset(context: AssetExecutionContext, dbt: DbtCliResource):
  """Runs the partitioned incremental model with date vars."""
  first_partition, last_partition = context.asset_partitions_time_window_for_output(
    list(context.selected_output_names)[0]
  )

  dbt_vars = {
    "start_date": str(first_partition),
    "end_date": str(last_partition),
  }

  dbt_args = ["build", "--vars", json.dumps(dbt_vars)]
  yield from dbt.cli(dbt_args, context=context).stream()
