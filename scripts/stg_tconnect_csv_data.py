import os
import pandas as pd
import duckdb
from io import StringIO
from dotenv import load_dotenv


# Paths
load_dotenv()
CSV_FOLDER = "C:/Users/krjam/dexcom/dexcom_glucose_analytics/seeds/data"
DB_PATH = "C:/Users/krjam/dexcom/dbt_duckdb_prod.db"
TABLE_NAME = "stg_tconnect_csv_data"
AUDIT_TABLE = "load_audit_log"

# Connect to DuckDB
con = duckdb.connect(DB_PATH)

# Create data table
con.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        reading_timestamp TIMESTAMP,
        glucose_mg_dl INTEGER
    )
""")

# Create audit table
con.execute(f"""
    CREATE TABLE IF NOT EXISTS {AUDIT_TABLE} (
        filename TEXT,
        raw_lines INTEGER,
        rows_loaded INTEGER,
        load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Aggregate data
combined_df = pd.DataFrame()

# Skip files that are already in the audit log
existing_files = con.execute(f"SELECT filename FROM {AUDIT_TABLE}").fetchdf()["filename"].tolist()

# Loop through files
for filename in os.listdir(CSV_FOLDER):
    if filename.endswith(".csv") and filename not in existing_files:
        full_path = os.path.join(CSV_FOLDER, filename)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                raw_lines = f.readlines()

            # Count raw data lines (excluding blank lines + header)
            expected_rows = sum(
                1 for line in raw_lines if line.strip() and "EventDateTime" not in line
            )

            # Remove trailing commas and blank lines
            cleaned_lines = [
                line.rstrip(",\n") + "\n" for line in raw_lines if line.strip()
            ]

            # Convert to DataFrame
            cleaned_csv = StringIO("".join(cleaned_lines))
            df = pd.read_csv(cleaned_csv)
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

            if {"EventDateTime", "Readings (mg/dL)"}.issubset(df.columns):
                cleaned = pd.DataFrame()
                cleaned["reading_timestamp"] = pd.to_datetime(df["EventDateTime"], errors="coerce")
                cleaned["glucose_mg_dl"] = pd.to_numeric(df["Readings (mg/dL)"], errors="coerce")
                cleaned.dropna(subset=["reading_timestamp", "glucose_mg_dl"], inplace=True)
                cleaned.drop_duplicates(subset=["reading_timestamp"], inplace=True)


                row_count = len(cleaned)
                combined_df = pd.concat([combined_df, cleaned], ignore_index=True)

                # Log to audit table
                con.execute(
                    f"INSERT INTO {AUDIT_TABLE} (filename, raw_lines, rows_loaded) VALUES (?, ?, ?)",
                    (filename, expected_rows, row_count)
                )

                print(f"{filename}: {row_count} loaded / {expected_rows} raw lines")

            else:
                print(f"Skipping {filename}: missing expected columns.")

        except Exception as e:
            print(f" Error reading {filename}:\n{e}")

# Final insert
# Only insert new rows
if not combined_df.empty:
    con.register("combined_df", combined_df)
    con.execute(f"INSERT INTO {TABLE_NAME} SELECT * FROM combined_df")


# Confirm and close
print(f"Total loaded: {len(combined_df)} rows into '{TABLE_NAME}'")
else_message = "No new data loaded."
if combined_df.empty:
    print(else_message)

con.close()
