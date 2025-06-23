import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# The user provided data is in CSV format, so let's define the columns
columns = ["device", "serial_number", "type", "timestamp", "value"]

file_path = r"C:\Users\krjam\Downloads\CSV_JamiesonKyle_1208369_22Jun2025_1557.csv"

# Create DataFrame
df = pd.read_csv(file_path)
df['reading_timestamp'] = pd.to_datetime(df['timestamp'])
df['glucose_mg_dl'] = pd.to_numeric(df['value'], errors='coerce')
df = df[['reading_timestamp', 'glucose_mg_dl']].dropna().reset_index(drop=True)

# Write to Parquet
parquet_file = r"C:\Users\krjam\Downloads\June_backfill.parquet"
df.to_parquet(parquet_file, index=False)

parquet_file
print(f"Parquet file saved to: {parquet_file}")
