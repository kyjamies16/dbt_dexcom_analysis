WITH source AS (
  SELECT
    CAST(
      "EventDateTime" AS TIMESTAMP
    ) AS reading_ts,
    CAST(
      "Readings (mg/dL)" AS INTEGER
    ) AS glucose_mg_dl
  FROM
    read_csv(
      '{{ var("tconnect_csv_path") }}',
      delim = ',',
      header = TRUE,
      quote = '"',
      ignore_errors = TRUE
    )
  WHERE
    CAST(
      "Readings (mg/dL)" AS INTEGER
    ) >= 0
)
SELECT
  *
FROM
  source
