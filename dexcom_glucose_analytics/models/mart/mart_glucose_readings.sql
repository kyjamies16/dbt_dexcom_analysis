SELECT
  reading_timestamp,
  reading_date,
  day_of_week,
  day_name,
  iso_week,
  month,
  year,
  week_start_date,
  month_start_date,
  hour_of_day,
  time_of_day_bucket,
  glucose_mg_dl,


  CASE 
    WHEN glucose_mg_dl < 70 THEN 'Low'
    WHEN glucose_mg_dl <= 180 THEN 'In Range'
    ELSE 'High'
  END AS glucose_range_label,

  CASE
    WHEN glucose_mg_dl BETWEEN 70 AND 180 THEN TRUE
    ELSE FALSE
  END AS is_in_range,

  LAG(glucose_mg_dl) OVER (ORDER BY reading_timestamp) AS previous_glucose,
  glucose_mg_dl - LAG(glucose_mg_dl) OVER (ORDER BY reading_timestamp) AS delta_glucose,

  AVG(glucose_mg_dl) OVER (
    PARTITION BY reading_date
  ) AS daily_avg_glucose

FROM {{ ref('int_dexcom_tconnect_union') }}
