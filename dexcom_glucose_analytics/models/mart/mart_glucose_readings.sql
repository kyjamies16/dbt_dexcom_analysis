{{ config(
  materialized='incremental',
  unique_key='reading_timestamp',
  on_schema_change='sync_all_columns'
) }}

{% set max_existing_ts %}
  {% if is_incremental() %}
    (SELECT MAX(reading_timestamp) FROM {{ this }})
  {% else %}
    '1900-01-01'  
  {% endif %}
{% endset %}

-- Dexcom staging data (from S3 parquet daily)
WITH dexcom AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl
  FROM {{ ref('stg_dexcom_readings') }}
  WHERE reading_timestamp > {{ max_existing_ts }}
),

-- t:connect staging data (from S3 parquet backfill)
tconnect AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl
  FROM {{ ref('stg_tconnect_readings') }}
  WHERE reading_timestamp > {{ max_existing_ts }}
),

-- Union them together & deduplicate by timestamp
combined AS (
  SELECT reading_timestamp, glucose_mg_dl FROM dexcom
  UNION ALL
  SELECT reading_timestamp, glucose_mg_dl FROM tconnect
),

deduped AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl,
    ROW_NUMBER() OVER (
      PARTITION BY reading_timestamp
      ORDER BY glucose_mg_dl DESC
    ) AS row_num
  FROM combined
)

-- Final output: only fresh, deduped records
SELECT
  reading_timestamp,
  glucose_mg_dl,
  CASE
    WHEN glucose_mg_dl BETWEEN 70
    AND 180 THEN TRUE
    ELSE FALSE
  END AS is_in_range,
  CAST(reading_timestamp AS DATE) AS reading_date,
  {{ time_bucket('reading_timestamp') }} AS time_of_day_bucket -- morning, afternoon, evening, night
  CASE
    WHEN glucose_mg_dl < 70 THEN 'Low'
    WHEN glucose_mg_dl <= 180 THEN 'In Range'
    ELSE 'High'
  END AS glucose_range_label
FROM deduped
WHERE row_num = 1
