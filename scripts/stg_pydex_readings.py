import logging
from pydexcom import Dexcom
import duckdb
import pandas as pd
from dotenv import load_dotenv
import os

def main():
    # Load env vars
    load_dotenv()
    DATABASE_PATH = os.getenv("DATABASE_PATH")
    USERNAME = os.getenv("DEXCOM_USERNAME")
    PASSWORD = os.getenv("DEXCOM_PASSWORD")

    # Set up logging (still file-based)
    logging.basicConfig(
        filename="glucose_ingest.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        dexcom = Dexcom(username=USERNAME, password=PASSWORD)
    except Exception as e:
        logging.error("Failed to authenticate with Dexcom", exc_info=True)
        raise RuntimeError("Dexcom auth failed") from e

    try:
        readings = dexcom.get_glucose_readings(1440)
    except Exception as e:
        logging.error(" Failed to fetch glucose readings", exc_info=True)
        raise RuntimeError("Dexcom fetch failed") from e

    if not readings:
        logging.info("⚠️ No glucose readings returned from Dexcom.")
        return 0

    df = pd.DataFrame(
        [(r.datetime, r.mg_dl) for r in readings],
        columns=["reading_ts", "glucose_mg_dl"]
    ).drop_duplicates(subset="reading_ts")

    logging.info(f"✅ Retrieved {len(df)} new readings from Dexcom.")

    try:
        with duckdb.connect(DATABASE_PATH) as con:
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
        logging.info(f"✅ Inserted {len(df)} new rows into stg_pydex_readings.")
        return len(df)
    except Exception as e:
        logging.error(" Failed to insert into DuckDB", exc_info=True)
        raise RuntimeError("DuckDB insert failed") from e

# Retain CLI fallback
if __name__ == "__main__":
    main()
