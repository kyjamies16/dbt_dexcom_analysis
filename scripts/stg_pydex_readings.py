import logging
from pydexcom import Dexcom
import duckdb
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    
    logging.basicConfig(
        filename='glucose_ingest.log', 
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

#Credentials
USERNAME = os.getenv("DEXCOM_USERNAME")
PASSWORD = os.getenv("DEXCOM_PASSWORD")

try:
    dexcom = Dexcom(username=USERNAME, password=PASSWORD)
    reading = dexcom.get_current_glucose_reading()
except Exception as e:
    msg = "❌ Failed to fetch glucose reading from Dexcom API"
    logging.error(msg, exc_info=True)
    print(msg, e)
    raise


df = pd.DataFrame([{
    "reading_ts": reading.datetime,
    "glucose_mg_dl": reading.mg_dl
}])


try:
    con = duckdb.connect("dbt_duckdb.db")
    con.execute("""
        CREATE TABLE IF NOT EXISTS stg_pydex_readings (
            reading_ts TIMESTAMP,
            glucose_mg_dl INTEGER
        )
    """)
    con.execute("INSERT INTO stg_pydex_readings SELECT * FROM df")
    logging.info(f"✅ Inserted new reading: {df.to_dict(orient='records')[0]}")
except Exception as e:
    msg = "❌ Failed to fetch glucose reading from Dexcom API"
    logging.error(msg, exc_info=True)
    print(msg, e)
    raise

