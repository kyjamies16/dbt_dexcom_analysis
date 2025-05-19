from dagster import asset
import subprocess
import os

@asset
def ingest_glucose_reading(context):
    script_path = os.path.abspath(
        os.path.join("..", "dexcom_glucose_analytics", "scripts", "stg_pydex_readings.py")
    )
    python_path = os.path.abspath(
        os.path.join("..", ".venv", "Scripts", "python.exe")
    )

    context.log.info(f"▶ Running: {python_path} {script_path}")

    try:
        result = subprocess.run(
            [python_path, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        context.log.info("✅ Script succeeded:")
        context.log.info(result.stdout)
    except subprocess.CalledProcessError as e:
        context.log.error("❌ Script failed!")
        context.log.error(">>> STDOUT:\n" + (e.stdout or ""))
        context.log.error(">>> STDERR:\n" + (e.stderr or ""))
        raise
