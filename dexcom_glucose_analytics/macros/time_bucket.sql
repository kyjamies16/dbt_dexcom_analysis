-- This group time buckets into four time periods: Morning, Afternoon, Evening, and Night.
{% macro time_bucket(column_name) %}
CASE
    WHEN EXTRACT(HOUR FROM {{column_name}}) BETWEEN 5 AND 11 THEN 'Morning'
    WHEN EXTRACT(HOUR FROM {{column_name}}) BETWEEN 12 AND 16 THEN 'Afternoon'
    WHEN EXTRACT(HOUR FROM {{column_name}}) BETWEEN 17 AND 20 THEN 'Evening'
    ELSE 'Night'
    END
{% endmacro %}