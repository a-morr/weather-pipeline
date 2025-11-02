"""Dagster sensors for event-driven pipeline execution."""

from dagster import sensor, RunRequest, SensorEvaluationContext, DefaultSensorStatus
from .assets import raw_weather_data
from .database import WeatherDatabase
from datetime import datetime, timedelta


@sensor(
    job_name="weather_ingestion_job",
    minimum_interval_seconds=300,  # Check every 5 minutes
    default_status=DefaultSensorStatus.STOPPED,
    description="Trigger ingestion if no data collected in last hour"
)
def stale_data_sensor(context: SensorEvaluationContext):
    """
    Sensor that triggers the pipeline if data is stale.

    This sensor checks if weather data hasn't been collected recently
    and triggers the ingestion job if needed.
    """
    db = WeatherDatabase()
    recent = db.get_recent_observations(limit=1)

    if not recent:
        context.log.info("No data found, triggering ingestion")
        yield RunRequest(run_key=f"initial_run_{datetime.now().isoformat()}")
        return

    latest_timestamp = datetime.fromisoformat(recent[0]["timestamp"])
    time_since_last = datetime.now() - latest_timestamp

    # If data is older than 1 hour, trigger ingestion
    if time_since_last > timedelta(hours=1):
        context.log.info(f"Data is stale ({time_since_last}), triggering ingestion")
        yield RunRequest(run_key=f"stale_data_{datetime.now().isoformat()}")
    else:
        context.log.info(f"Data is fresh ({time_since_last} old)")
