import os
import pandas as pd
import boto3
from datetime import datetime
from dagster import AssetExecutionContext, asset, MetadataValue
from dotenv import load_dotenv
from pydexcom import Dexcom
from zoneinfo import ZoneInfo
from ..core_constants import dotenv_path

load_dotenv(dotenv_path) 

@asset
def ingest_glucose_readings(context: AssetExecutionContext):
    """
    Fetch Dexcom readings & write them as Parquet to S3.
    """

    # Env vars
    username = os.getenv("DEXCOM_USERNAME")
    password = os.getenv("DEXCOM_PASSWORD")
    bucket = os.getenv("AWS_S3_BUCKET_NAME")
    print("AWS_S3_BUCKET_NAME =", bucket)



    if not username or not password or not bucket:
        raise ValueError("Missing DEXCOM_USERNAME, DEXCOM_PASSWORD, or BUCKET_NAME")

    # Fetch Dexcom readings
   
    dexcom = Dexcom(username=username, password=password)
    readings = dexcom.get_glucose_readings(1440)

    if not readings:
        context.log.info("⚠️ No glucose readings returned.")
        return

    #3 Make DataFrame
    df = pd.DataFrame(
        [(r.datetime, r.mg_dl) for r in readings],
        columns=["reading_ts", "glucose_mg_dl"]
    ).drop_duplicates(subset="reading_ts")

    # Write to local Parquet
    now = datetime.now(ZoneInfo("US/Central")).strftime("%Y-%m-%d-%H%M%S")
    local_file = f"glucose_{now}.parquet"
    df.to_parquet(local_file, index=False)

    # Upload to S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    s3_key = f"glucose_readings/{local_file}"

    s3.upload_file(local_file, bucket, s3_key, ExtraArgs={"ACL": "bucket-owner-full-control"})

    context.log.info(f"✅ Uploaded new Parquet: s3://{bucket}/{s3_key}")

    context.add_output_metadata({
        "row_count": len(df),
        "latest_timestamp": str(df['reading_ts'].max()),
        "preview": MetadataValue.md(df.head().to_markdown()),
        "s3_key": s3_key,
    })
