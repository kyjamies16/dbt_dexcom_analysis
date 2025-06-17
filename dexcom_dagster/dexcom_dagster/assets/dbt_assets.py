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


# --------------------------
# ✅ ONE partition definition
# --------------------------
daily_partitions = DailyPartitionsDefinition(start_date="2025-05-19", timezone="US/Central")

# --------------------------
# ✅ ONE custom translator with partition_expr
# --------------------------
class PartitionAwareDbtTranslator(DagsterDbtTranslator):
    def get_metadata(self, dbt_resource_props: Mapping[str, Any]) -> Mapping[str, Any]:
        metadata = {"partition_expr": "reading_date"}
        default_metadata = default_metadata_from_dbt_resource_props(dbt_resource_props)
        return {**default_metadata, **metadata}

# --------------------------
# ✅ SINGLE dbt_assets for ALL models
# --------------------------
@dbt_assets(
    manifest=dbt_manifest_path,
    partitions_def=daily_partitions,
    dagster_dbt_translator=PartitionAwareDbtTranslator(),
)
def all_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    Runs ALL dbt models, with partitioned vars (start_date, end_date).
    Ensures the incremental int_glucose_readings_combined runs in sequence
    with all other dependent models.
    """
    # This works because the partition_expr tells Dagster which column to partition by
    first_partition, last_partition = context.asset_partitions_time_window_for_output(
        list(context.selected_output_names)[0]
    )

    dbt_vars = {
        "start_date": str(first_partition),
        "end_date": str(last_partition),
    }

    dbt_args = ["build", "--vars", json.dumps(dbt_vars)]
    yield from dbt.cli(dbt_args, context=context).stream()
