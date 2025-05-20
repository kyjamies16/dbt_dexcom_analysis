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
    reading_ts AS reading_timestamp,
    glucose_mg_dl AS glucose_mg_dl
  FROM
    source
)
SELECT
  *
FROM
  renamed
