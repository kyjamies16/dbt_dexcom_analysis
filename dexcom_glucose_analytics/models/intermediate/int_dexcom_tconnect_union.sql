SELECT
  *
FROM
  (
    SELECT
      reading_timestamp,
      glucose_mg_dl
    FROM
      {{ ref('stg_dexcom_readings') }}
    UNION ALL
    SELECT
      reading_timestamp,
      glucose_mg_dl
    FROM
      {{ ref('stg_tconnect_readings') }}
  ) AS unioned_readings
