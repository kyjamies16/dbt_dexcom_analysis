import os
import duckdb
from datetime import datetime, timezone
from typing import Mapping, Any
from dagster import MetadataValue
from dagster_dbt import DagsterDbtTranslator, default_metadata_from_dbt_resource_props

# Use DATABASE_PATH from environment or fallback to default DuckDB path
DB_PATH = os.getenv("DATABASE_PATH", "C:/Users/krjam/dexcom/dbt_duckdb_prod.db")

class CustomDagsterDbtTranslator(DagsterDbtTranslator):
    def get_metadata(self, dbt_resource_props: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Injects model-level metadata for Dagster UI, including:
        - Preview of 5 most recent rows (if available)
        - Row count
        - Timestamp freshness based on `reading_ts`
        """
        metadata = default_metadata_from_dbt_resource_props(dbt_resource_props)

        # Only enrich metadata for dbt models
        if dbt_resource_props.get("resource_type") != "model":
            return metadata

        model_name = dbt_resource_props.get("name")
        schema = dbt_resource_props.get("schema")
        table = f"{schema}.{model_name}"

        try:
            con = duckdb.connect(DB_PATH)
            df = con.execute(f"SELECT * FROM {table} ORDER BY reading_ts DESC LIMIT 5").fetchdf()

            metadata["preview"] = MetadataValue.md(df.to_markdown(index=False))
            metadata["row_count"] = MetadataValue.int(len(df))

            if not df.empty and "reading_ts" in df.columns:
                latest_ts = df["reading_ts"].max()
                metadata["latest_timestamp"] = MetadataValue.timestamp(latest_ts.timestamp())
                metadata["freshness"] = MetadataValue.text(str(datetime.now(timezone.utc) - latest_ts))

        except Exception as e:
            metadata["preview"] = MetadataValue.text(f"Metadata fetch error: {str(e)}")

        return metadata