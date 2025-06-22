import os
import duckdb
import boto3
from dagster import asset, MetadataValue, Output, Failure
from ..core_constants import DB_PATH

@asset
def export_glucose_to_parquet_and_upload(context):
    """
    1) Downloads the latest DuckDB file from S3
    2) Exports mart_glucose_readings to Parquet
    3) Uploads Parquet back to S3
    """

    # Load config from env
    db_path = DB_PATH  # e.g., "dbt_duckdb_prod.db"
    db_s3_key = os.getenv("DBT_DUCKDB_FILENAME", "dbt_duckdb_prod.db")
    parquet_file = os.getenv("PARQUET_FILENAME", "mart_glucose_readings.parquet")
    bucket_name = os.getenv("AWS_S3_BUCKET_NAME")

    if not bucket_name:
        raise Failure("AWS_S3_BUCKET_NAME is not set.")

    context.log.info(f"Using bucket={bucket_name}, db_path={db_path}")

    # Step 1: Download the updated DuckDB DB from S3
    try:
        context.log.info(f"Downloading {db_s3_key} from S3 to local {db_path}")
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        s3.download_file(bucket_name, db_s3_key, db_path)
        context.log.info("Download complete.")
    except Exception as e:
        context.log.error(f"Failed to download DuckDB: {e}")
        raise Failure(f"Failed to download DuckDB file: {e}")

    # Step 2: Export table to Parquet
    try:
        context.log.info(f"Exporting table to Parquet: {parquet_file}")
        con = duckdb.connect(db_path)
        con.execute(f"""
            COPY main_mart.mart_glucose_readings
            TO '{parquet_file}'
            (FORMAT PARQUET, OVERWRITE TRUE)
        """)
        con.close()
        context.log.info(f"Export complete: {parquet_file}")
    except Exception as e:
        context.log.error(f"Failed export: {e}")
        raise Failure(f"Failed to export table: {e}")

    # Step 3: Upload Parquet to S3
    try:
        context.log.info(f"Uploading Parquet to S3: s3://{bucket_name}/{parquet_file}")
        s3.upload_file(
            Filename=parquet_file,
            Bucket=bucket_name,
            Key=parquet_file,
            ExtraArgs={'ACL': 'public-read'}
        )
        context.log.info(f"Upload complete.")
    except Exception as e:
        context.log.error(f"Failed upload: {e}")
        raise Failure(f"Failed to upload Parquet: {e}")

    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{parquet_file}"

    return Output(
        value=s3_url,
        metadata={
            "output_file": parquet_file,
            "s3_url": MetadataValue.url(s3_url),
            "bucket": bucket_name
        }
    )
