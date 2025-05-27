{{ config(
  materialized='incremental',
  unique_key='reading_timestamp'
) }}

WITH frozen_backfill AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl
  FROM "dbt_duckdb"."main_intermediate"."int_glucose_readings_backfill"
),

dexcom_new AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl
  FROM {{ ref('stg_dexcom_readings') }}
  {% if is_incremental() %}
    WHERE reading_timestamp > (
      SELECT MAX(reading_timestamp)
      FROM {{ this }}
    )
  {% else %}
    WHERE reading_timestamp >= '2025-05-19'
  {% endif %}
),

unioned_readings AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl,
    ROW_NUMBER() OVER (PARTITION BY reading_timestamp ORDER BY reading_timestamp) AS row_num
  FROM (
    SELECT reading_timestamp, glucose_mg_dl FROM frozen_backfill
    UNION ALL
    SELECT reading_timestamp, glucose_mg_dl FROM dexcom_new
  )
)

SELECT
  reading_timestamp,
  glucose_mg_dl,

  -- Date metadata
  CAST(reading_timestamp AS DATE) AS reading_date,
  EXTRACT(DAYOFWEEK FROM reading_timestamp) AS day_of_week,
  STRFTIME(reading_timestamp, '%w') AS day_name,
  EXTRACT(WEEK FROM reading_timestamp) AS iso_week,
  EXTRACT(MONTH FROM reading_timestamp) AS month,
  EXTRACT(YEAR FROM reading_timestamp) AS year,
  DATE_TRUNC('week', reading_timestamp) AS week_start_date,
  DATE_TRUNC('month', reading_timestamp) AS month_start_date,

  -- Time metadata
  EXTRACT(HOUR FROM reading_timestamp) AS hour_of_day,
  {{ time_bucket('reading_timestamp') }} AS time_of_day_bucket

FROM unioned_readings
WHERE row_num = 1
