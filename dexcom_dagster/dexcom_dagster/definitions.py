# definitions.py
from dagster import Definitions

from .assets.ingest_glucose_readings import ingest_glucose_readings
from .assets.dbt_assets import debug_dbt_asset
from .jobs.glucose_ingest_job import glucose_ingest_job
from .jobs.materialize_dbt_job import materialize_dbt_job
from .schedules.schedules import schedules
from .constants import dbt  

defs = Definitions(
    assets=[
        debug_dbt_asset,
        ingest_glucose_readings,
    ],
    jobs=[
        glucose_ingest_job,
        materialize_dbt_job,
    ],
    schedules=schedules,
    resources={
        "dbt": dbt,  
    },
)
