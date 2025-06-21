import os
import pandas as pd
import boto3
import duckdb
from dotenv import load_dotenv
from pathlib import Path

# ------------------------------------
# 1️⃣ Load .env.prod from repo root
# ------------------------------------
dotenv_path = Path(__file__).resolve().parent.parent / ".env.prod"
load_dotenv(dotenv_path=dotenv_path)

# ------------------------------------
# 2️⃣ Get AWS creds + bucket
# ------------------------------------
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
bucket = os.getenv("AWS_S3_BUCKET_NAME")

print(f"AWS_S3_BUCKET_NAME = {bucket}")

if not aws_access_key_id or not aws_secret_access_key or not bucket:
    raise ValueError("Missing AWS credentials or bucket name!")

# ------------------------------------
# 3️⃣ Connect to DuckDB & pull t_connect table
# ------------------------------------
con = duckdb.connect("dbt_duckdb_prod.db")

df = con.execute("SELECT * FROM main.stg_tconnect_csv_data").df()
print(f"✅ Loaded {len(df):,} rows from stg_tconnect_csv_data")

# ------------------------------------
# 4️⃣ Write to local Parquet
# ------------------------------------
backfill_file = "tconnect_backfill.parquet"
df.to_parquet(backfill_file, index=False)
print(f"✅ Saved to {backfill_file}")

# ------------------------------------
# 5️⃣ Upload to S3 under a clear folder
# ------------------------------------
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

s3_key = f"t_connect/{backfill_file}"

s3.upload_file(
    Filename=backfill_file,
    Bucket=bucket,
    Key=s3_key,
    ExtraArgs={"ACL": "private"},
)

print(f"✅ Uploaded to s3://{bucket}/{s3_key}")
