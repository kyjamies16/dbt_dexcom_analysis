WITH source AS (
  SELECT
    *
  FROM {{ source('dexcom', 'dexcom_glucose_readings') }}
),

renamed AS (
  SELECT
    CAST(reading_ts AS TIMESTAMP) AS reading_timestamp,
    CAST(glucose_mg_dl AS INTEGER) AS glucose_mg_dl
  FROM source
),

deduplicated AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl,
    ROW_NUMBER() OVER (
      PARTITION BY reading_timestamp
      ORDER BY glucose_mg_dl  
    ) AS row_num
  FROM renamed
)

SELECT
  reading_timestamp,
  glucose_mg_dl
FROM
  deduplicated
WHERE
  row_num = 1
