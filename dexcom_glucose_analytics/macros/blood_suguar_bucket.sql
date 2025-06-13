-- Buckets blood glucose values into Low, Normal, High
{% macro blood_sugar_bucket(column_name) %}
CASE
    WHEN {{ column_name }} < 70 THEN 'Low'
    WHEN {{ column_name }} BETWEEN 70 AND 180 THEN 'Normal'
    WHEN {{ column_name }} > 180 THEN 'High'
    ELSE 'Unknown'
END
{% endmacro %}
