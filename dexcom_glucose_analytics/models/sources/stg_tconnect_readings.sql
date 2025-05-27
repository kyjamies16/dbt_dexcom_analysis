WITH source AS(
  SELECT
    *
  FROM
    {{ source(
      't_connect',
      't_connect_glucose_readings'
    ) }}
),
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
