WITH date_range AS (
  SELECT
    MIN(CAST(reading_timestamp AS DATE)) AS start_date,
    MAX(CAST(reading_timestamp AS DATE)) AS end_date
  FROM
    {{ ref('int_glucose_readings_combined') }}
),

expected_dates AS (
  SELECT
    DATE_TRUNC('day', date) AS reading_date
  FROM
    generate_series(
      (SELECT start_date FROM date_range),
      (SELECT end_date FROM date_range),
      INTERVAL '1 day'
    ) AS t(date)
),

actual_dates AS (
  SELECT
    DISTINCT CAST(reading_timestamp AS DATE) AS reading_date
  FROM
    {{ ref('int_glucose_readings_combined') }}
)

SELECT
  expected_dates.reading_date
FROM
  expected_dates
  LEFT JOIN actual_dates
  ON expected_dates.reading_date = actual_dates.reading_date
WHERE
  actual_dates.reading_date IS NULL
