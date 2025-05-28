from dagster import op
import subprocess, os
from pathlib import Path
from dotenv import load_dotenv

@op
def run_glucose_script(context):
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
    script_path = os.path.abspath("dexcom_glucose_analytics/scripts/stg_pydex_readings.py")
    python_path = os.path.abspath(".venv/Scripts/python.exe")

    context.log.info(f"Running: {python_path} {script_path}")
    result = subprocess.run([python_path, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        context.log.error(result.stderr)
        raise Exception("Script failed")
    context.log.info(result.stdout)
