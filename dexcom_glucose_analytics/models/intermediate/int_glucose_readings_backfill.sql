WITH dexcom_readings AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl
  FROM {{ ref('stg_dexcom_readings') }}
),

tconnect_readings AS (
  SELECT
    reading_timestamp,
    glucose_mg_dl
  FROM {{ ref('stg_tconnect_readings') }}
),

unioned_readings AS (
  SELECT * FROM dexcom_readings
  UNION ALL
  SELECT * FROM tconnect_readings
)

SELECT
  reading_timestamp,
  glucose_mg_dl,

  -- Date metadata 
  reading_timestamp AS reading_date,
  STRFTIME(reading_timestamp, '%w')::INTEGER AS day_of_week,  
  STRFTIME(reading_timestamp, '%A') AS day_name,
  STRFTIME(reading_timestamp, '%W')::INTEGER AS iso_week,         
  STRFTIME(reading_timestamp, '%m')::INTEGER AS month,
  STRFTIME(reading_timestamp, '%Y')::INTEGER AS year,
  DATE_TRUNC('week', reading_timestamp) AS week_start_date,
  DATE_TRUNC('month', reading_timestamp) AS month_start_date,

  -- Time metadata
  STRFTIME(reading_timestamp, '%H')::INTEGER AS hour_of_day,
  {{ time_bucket('reading_timestamp') }} AS time_of_day_bucket

FROM unioned_readings
