import os
import duckdb
import boto3
from dagster import asset, MetadataValue, Output, Failure

@asset
def export_glucose_to_parquet_and_upload(context):
    """
    Dagster asset:
    1) Exports DuckDB table to Parquet
    2) Uploads Parquet to S3 with public-read
    3) Logs each step in Dagster UI
    """

    # Load config from env
    db_path = os.getenv("DATABASE_PATH", "dbt_duckdb_prod.db")
    parquet_file = os.getenv("PARQUET_FILENAME", "mart_glucose_readings.parquet")
    bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
    s3_object_name = parquet_file

    if not bucket_name:
        raise Failure("AWS_S3_BUCKET_NAME is not set in environment variables.")

    context.log.info(f"Loaded config: db_path={db_path}, bucket={bucket_name}")

    # Step 1: Export DuckDB → Parquet
    try:
        context.log.info(f"Exporting table to Parquet: {parquet_file}")
        con = duckdb.connect(db_path)
        con.execute(f"""
            COPY main_mart.mart_glucose_readings
            TO '{parquet_file}'
            (FORMAT PARQUET, OVERWRITE TRUE)
        """)
        context.log.info(f"Export complete: {parquet_file}")

    except Exception as e:
        context.log.error(f" Failed export: {e}")
        raise Failure(
            description="Failed to export DuckDB table to Parquet.",
            metadata={"error": str(e)}
        )

    # Step 2: Upload to S3
    try:
        context.log.info(f"Uploading Parquet to S3: s3://{bucket_name}/{s3_object_name}")

        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        s3.upload_file(
            Filename=parquet_file,
            Bucket=bucket_name,
            Key=s3_object_name,
            ExtraArgs={'ACL': 'public-read'}
        )

        context.log.info(f"Upload complete: s3://{bucket_name}/{s3_object_name}")

    except Exception as e:
        context.log.error(f"Failed upload: {e}")
        raise Failure(
            description="Failed to upload Parquet to S3.",
            metadata={"error": str(e)}
        )

    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_object_name}"

    context.log.info(f"Public S3 URL: {s3_url}")

    context.log.info(f"Successfully exported and uploaded to S3: {s3_url}")
    return Output(
        value=s3_url,
        metadata={
            "output_file": parquet_file,
            "s3_url": MetadataValue.url(s3_url),
            "bucket": bucket_name
        }
    )
