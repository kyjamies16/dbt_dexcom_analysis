from pathlib import Path

from dagster_dbt import DbtProject

dexcom_glucose_analytics_project = DbtProject(
    project_dir=Path(__file__).joinpath("..", "..", "..", "dexcom_glucose_analytics").resolve(),
    packaged_project_dir=Path(__file__).joinpath("..", "..", "dbt-project").resolve(),
)
dexcom_glucose_analytics_project.prepare_if_dev()