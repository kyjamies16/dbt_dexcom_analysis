import os
import pandas as pd
import duckdb
from dagster import AssetExecutionContext, asset, MetadataValue
from dotenv import load_dotenv
from pydexcom import Dexcom

load_dotenv()

@asset
def ingest_glucose_readings(context: AssetExecutionContext) -> pd.DataFrame:
    # Load credentials and DB path
    username = os.getenv("DEXCOM_USERNAME")
    password = os.getenv("DEXCOM_PASSWORD")
    db_path = os.getenv("DATABASE_PATH")

    if not username or not password or not db_path:
        raise ValueError("Missing one or more environment variables: DEXCOM_USERNAME, DEXCOM_PASSWORD, DATABASE_PATH")

    # Fetch from Dexcom
    try:
        dexcom = Dexcom(username=username, password=password)
        readings = dexcom.get_glucose_readings(1440)
    except Exception as e:
        context.log.error("Dexcom authentication or fetch failed", exc_info=True)
        raise

    if not readings:
        context.log.info("⚠️ No glucose readings returned from Dexcom.")
        return pd.DataFrame()

    # Build DataFrame
    df = pd.DataFrame(
        [(r.datetime, r.mg_dl) for r in readings],
        columns=["reading_ts", "glucose_mg_dl"]
    ).drop_duplicates(subset="reading_ts")

    # Insert new readings into DuckDB
    try:
        with duckdb.connect(db_path) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS stg_pydex_readings (
                    reading_ts TIMESTAMP,
                    glucose_mg_dl INTEGER
                )
            """)
            con.register("df", df)
            con.execute("CREATE OR REPLACE TEMP TABLE new_data AS SELECT * FROM df")
            con.execute("""
                INSERT INTO stg_pydex_readings
                SELECT * FROM new_data
                WHERE NOT EXISTS (
                    SELECT 1 FROM stg_pydex_readings
                    WHERE stg_pydex_readings.reading_ts = new_data.reading_ts
                )
            """)
    except Exception as e:
        context.log.error("Failed to insert into DuckDB", exc_info=True)
        raise

    context.log.info(f"✅ Inserted {len(df)} new rows into stg_pydex_readings.")

    context.add_output_metadata({
        "row_count": len(df),
        "latest_timestamp": str(df['reading_ts'].max()),
        "preview": MetadataValue.md(df.head().to_markdown())
    })

    return df
