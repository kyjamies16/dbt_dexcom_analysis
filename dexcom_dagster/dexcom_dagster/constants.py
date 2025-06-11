from pathlib import Path
from dagster_dbt import DbtCliResource

dbt_project_dir = Path("C:/Users/krjam/dexcom/dexcom_glucose_analytics")

dbt = DbtCliResource(
    project_dir=str(dbt_project_dir),
    profiles_dir="C:/Users/krjam/.dbt",
    working_directory=str(dbt_project_dir),
)
dbt_manifest_path = dbt_project_dir / "target" / "manifest.json"
