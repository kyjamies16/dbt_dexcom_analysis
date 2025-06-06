# config/settings.py

from datetime import date, timedelta

# Default chart date range
DEFAULT_DAYS_BACK = 7
DEFAULT_START_DATE = date.today() - timedelta(days=DEFAULT_DAYS_BACK)
DEFAULT_END_DATE = date.today()

# Glucose thresholds
GLUCOSE_LOW = 70
GLUCOSE_HIGH = 180

# Streamlit app config
APP_TITLE = "Glucose Overview"
CSV_FILENAME = "glucose_data.csv"

# Chart config
TIME_BUCKET_MINUTES = 30
TOOLTIP_ROUND_DECIMALS = 1
Y_AXIS_MAX_PADDING = 10

# Date format (for display, not necessarily datetime formatting)
DISPLAY_DATE_FORMAT = "%b %d, %Y"

# Format for displaying the last glucose reading time, e.g., "Jun 10, 2024 at 03:45 PM"
LAST_TIME_FORMAT = "%b %d, %Y at %I:%M %p"

TOOLTIP_HINT = "💡 Tip: Right-click the chart to save it as an image."
