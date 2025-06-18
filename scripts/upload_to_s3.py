import boto3


BUCKET_NAME = 'chumbucket4356'
FILE_PATH = 'C:/Users/krjam/dexcom/mart_glucose_readings.parquet'
OBJECT_NAME = 'mart_glucose_readings.parquet'

# This uses your local AWS credentials (~/.aws/credentials)
s3 = boto3.client('s3')

# Upload
s3.upload_file(FILE_PATH, BUCKET_NAME, OBJECT_NAME)

print(f"Uploaded {FILE_PATH} to s3://{BUCKET_NAME}/{OBJECT_NAME}")
