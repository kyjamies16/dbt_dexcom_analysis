import logging
from pydexcom import Dexcom
import duckdb
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Debug print to confirm .env is working
print(f"[DEBUG - ingest script] DATABASE_PATH = {os.getenv('DATABASE_PATH')}")

# Use env var for DB path
DATABASE_PATH = os.getenv("DATABASE_PATH")

# Setup logging
logging.basicConfig(
    filename='glucose_ingest.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # Get Dexcom credentials
    USERNAME = os.getenv("DEXCOM_USERNAME")
    PASSWORD = os.getenv("DEXCOM_PASSWORD")

    try:
        dexcom = Dexcom(username=USERNAME, password=PASSWORD)
        reading = dexcom.get_current_glucose_reading()
        
        if reading is None:
            msg = "Dexcom returned no current glucose reading."
            logging.warning(msg)
            print(msg)
            exit(0)
    except Exception as e:
        msg = "Failed to fetch glucose reading from Dexcom API"
        logging.error(msg, exc_info=True)
        print(msg, e)
        raise

    # Create DataFrame
    df = pd.DataFrame([{
        "reading_ts": reading.datetime,
        "glucose_mg_dl": reading.mg_dl
    }])

# Insert into DuckDB
try:
  with duckdb.connect(DATABASE_PATH) as con:
    # Create table if it doesn't exist
    con.execute("""
      CREATE TABLE IF NOT EXISTS stg_pydex_readings (
        reading_ts TIMESTAMP,
        glucose_mg_dl INTEGER
      )
    """)

    # Insert only if not already present
    con.execute("""
      INSERT INTO stg_pydex_readings
      SELECT * FROM df
      WHERE NOT EXISTS (
        SELECT 1 FROM stg_pydex_readings
        WHERE stg_pydex_readings.reading_ts = df.reading_ts
      )
    """)

    # Log success
    logging.info(f"Inserted new reading: {df.to_dict(orient='records')[0]}")
except Exception as e:
  msg = "Failed to insert glucose reading into DuckDB"
  logging.error(msg, exc_info=True)
  print(msg, e)
  raise
