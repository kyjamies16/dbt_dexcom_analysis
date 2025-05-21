WITH source AS (
  SELECT
    *
  FROM
    {{ source(
      'dexcom',
      'glucose_readings'
    ) }}
),
renamed AS (
  SELECT
    CAST(
      reading_ts AS TIMESTAMP
    ) AS reading_timestamp,
    CAST(
      glucose_mg_dl AS INTEGER
    ) AS glucose_mg_dl
  FROM
    source
)
SELECT
  *
FROM
  renamed
