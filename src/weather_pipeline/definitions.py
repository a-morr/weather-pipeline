"""Dagster definitions - the main entry point for the pipeline."""

from dagster import (
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    AssetSelection,
)

from .assets import raw_weather_data, stored_weather_data, weather_summary


# Define a job that materializes all weather ingestion assets
weather_ingestion_job = define_asset_job(
    name="weather_ingestion_job",
    selection=AssetSelection.groups("weather_ingestion", "weather_reporting"),
    description="Fetch weather data and store in database"
)

# Define a schedule to run the job every hour
hourly_weather_schedule = ScheduleDefinition(
    job=weather_ingestion_job,
    cron_schedule="0 * * * *",  # Every hour at minute 0
    description="Run weather ingestion every hour"
)

# You can also create a more frequent schedule for testing/learning
frequent_weather_schedule = ScheduleDefinition(
    job=weather_ingestion_job,
    cron_schedule="*/15 * * * *",  # Every 15 minutes
    description="Run weather ingestion every 15 minutes (for testing)"
)


# This is the main entry point that Dagster looks for
defs = Definitions(
    assets=[raw_weather_data, stored_weather_data, weather_summary],
    jobs=[weather_ingestion_job],
    schedules=[hourly_weather_schedule, frequent_weather_schedule],
)
