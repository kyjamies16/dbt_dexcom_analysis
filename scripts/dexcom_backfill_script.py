import os
import pandas as pd
import boto3
import duckdb
import os
from dotenv import load_dotenv
from pathlib import Path

# Resolve absolute path to .env.prod
dotenv_path = Path(__file__).resolve().parent.parent / ".env.prod"
print(dotenv_path)

# Load it
load_dotenv(dotenv_path=dotenv_path)

# Load credentials
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
print("AWS_ACCESS_KEY_ID =", aws_access_key_id)

aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
bucket = os.getenv("AWS_S3_BUCKET_NAME")
print("AWS_S3_BUCKET_NAME =", bucket)


# Connect to DuckDB
con = duckdb.connect("dbt_duckdb_prod.db")

# Pull the full staging table
df = con.execute("SELECT * FROM stg_pydex_readings").df()
print(f"✅ Loaded {len(df):,} rows from local DuckDB")

# Write to a backfill Parquet file
backfill_file = "glucose_backfill.parquet"
df.to_parquet(backfill_file, index=False)
print(f"✅ Saved to {backfill_file}")

# Upload to S3
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

s3.upload_file(
    Filename=backfill_file,
    Bucket=bucket,  
    Key=f"glucose_exports/{backfill_file}",
    ExtraArgs={"ACL": "private"}
)

print(f"✅ Uploaded to s3://{bucket}/glucose_exports/{backfill_file}")
