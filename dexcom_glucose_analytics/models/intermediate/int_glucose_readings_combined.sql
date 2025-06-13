{{ config(
  materialized='incremental',
  unique_key='reading_timestamp'
) }}

{#—
  These variables allow the model to be run for a specific date range,
  as passed in by Dagster through `--vars` (e.g., for daily partitions).
  Default values ensure local runs won't fail.
—#}
{% set start_date = var('start_date', '2025-01-01') %}
{% set end_date = var('end_date', '2099-12-31') %}

-- Pull in the "frozen" backfill data from a static table
WITH frozen_backfill AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl
  FROM main_intermediate.int_glucose_readings_backfill
),

-- Pull in new data from the staging table, filtered by the given partition window
dexcom_new AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl
  FROM {{ ref('stg_dexcom_readings') }}
  WHERE reading_timestamp >= '{{ start_date }}'
    AND reading_timestamp < '{{ end_date }}'
),

-- Union the frozen and new data, deduplicating by reading_timestamp
unioned_readings AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl,
    ROW_NUMBER() OVER (
      PARTITION BY reading_timestamp
      ORDER BY reading_timestamp
    ) AS row_num
  FROM (
    SELECT reading_timestamp, glucose_mg_dl FROM frozen_backfill
    UNION ALL
    SELECT reading_timestamp, glucose_mg_dl FROM dexcom_new
  )
)

-- Final output: filter to keep only the first record per timestamp,
-- and add date/time metadata for downstream analytics
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
