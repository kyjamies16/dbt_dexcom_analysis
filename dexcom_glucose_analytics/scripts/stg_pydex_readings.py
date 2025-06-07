import logging
from pydexcom import Dexcom
import duckdb
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
DATABASE_PATH = os.getenv("DATABASE_PATH")
USERNAME = os.getenv("DEXCOM_USERNAME")
PASSWORD = os.getenv("DEXCOM_PASSWORD")

# Setup logging
logging.basicConfig(
    filename="glucose_ingest.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    try:
        dexcom = Dexcom(username=USERNAME, password=PASSWORD)
    except Exception as e:
        msg = "Failed to authenticate with Dexcom"
        logging.error(msg, exc_info=True)
        print(msg, e)
        return

    try:
        readings = dexcom.get_glucose_readings(1440)  # last 24 hours
    except Exception as e:
        msg = "Failed to fetch glucose readings"
        logging.error(msg, exc_info=True)
        print(msg, e)
        return

    if not readings:
        logging.info("No glucose readings returned from Dexcom.")
        return

    # Build dataframe
    df = pd.DataFrame([(r.datetime, r.mg_dl) for r in readings],
                      columns=["reading_ts", "glucose_mg_dl"])
    df.drop_duplicates(subset="reading_ts", inplace=True)

    logging.info(f"Retrieved {len(df)} new readings from Dexcom.")

    # Insert into DuckDB
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

            logging.info(f"Inserted {len(df)} new rows into stg_pydex_readings.")
    except Exception as e:
        msg = "Failed to insert readings into DuckDB"
        logging.error(msg, exc_info=True)
        print(msg, e)

if __name__ == "__main__":
    main()
