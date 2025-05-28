from dagster import op
import subprocess, os
from dotenv import load_dotenv
from pathlib import Path

@op
def run_dbt(context):
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
    result = subprocess.run(
        ["dbt", "build", "--project-dir", "dexcom_glucose_analytics"],
        capture_output=True, text=True, env=os.environ.copy()
    )
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise Exception("DBT run failed")
    context.log.info(result.stdout)
