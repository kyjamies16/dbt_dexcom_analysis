WITH source AS(
  SELECT
    *
  FROM read_parquet('s3://chumbucket4356/t_connect/*.parquet')),

renamed AS (
  SELECT
    CAST(
      reading_timestamp AS TIMESTAMP
    ) AS reading_timestamp,
    CAST(
      glucose_mg_dl AS INTEGER
    ) AS glucose_mg_dl
  FROM
    source
)
SELECT
  DISTINCT
  reading_timestamp,
  glucose_mg_dl,
FROM
  renamed
