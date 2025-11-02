"""Dagster assets for weather data ingestion pipeline."""

from dagster import asset, AssetExecutionContext, Output, MetadataValue
from typing import Dict, Any
import pandas as pd

from .weather_api import WeatherAPIClient
from .database import WeatherDatabase
from .config import CITY_NAME


@asset(
    description="Fetch current weather data from Open-Meteo API",
    group_name="weather_ingestion"
)
def raw_weather_data(context: AssetExecutionContext) -> Dict[str, Any]:
    """
    Fetch current weather data from the API.

    This asset calls the Open-Meteo API to get the latest weather conditions.
    """
    context.log.info(f"Fetching weather data for {CITY_NAME}")

    client = WeatherAPIClient()
    weather_data = client.fetch_current_weather()

    context.log.info(f"Successfully fetched weather data: {weather_data['temperature_f']}°F")

    return weather_data


@asset(
    description="Store weather data in SQLite database",
    group_name="weather_ingestion",
    deps=[raw_weather_data]
)
def stored_weather_data(
    context: AssetExecutionContext,
    raw_weather_data: Dict[str, Any]
) -> Output[Dict[str, Any]]:
    """
    Store weather data in the local SQLite database.

    This asset takes the raw weather data and persists it to the database.
    """
    db = WeatherDatabase()

    context.log.info("Inserting weather data into database")
    row_id = db.insert_weather_data(raw_weather_data)

    if row_id == -1:
        context.log.warning("Duplicate weather data detected, skipping insert")
        status = "duplicate"
    else:
        context.log.info(f"Weather data inserted with ID: {row_id}")
        status = "inserted"

    # Get database statistics for metadata
    stats = db.get_database_stats()

    return Output(
        value={
            "status": status,
            "row_id": row_id,
            "timestamp": raw_weather_data["timestamp"],
            "temperature_f": raw_weather_data["temperature_f"]
        },
        metadata={
            "status": status,
            "total_records": stats["total_records"],
            "database_size_mb": round(stats["database_size_mb"], 2),
            "temperature_f": raw_weather_data["temperature_f"],
            "humidity_percent": raw_weather_data["humidity_percent"],
        }
    )


@asset(
    description="Weather data quality report",
    group_name="weather_reporting",
    deps=[stored_weather_data]
)
def weather_summary(context: AssetExecutionContext) -> Output[pd.DataFrame]:
    """
    Generate a summary report of recent weather observations.

    This asset creates a pandas DataFrame with recent weather data for analysis.
    """
    db = WeatherDatabase()

    context.log.info("Generating weather summary report")

    # Get recent observations
    recent_data = db.get_recent_observations(limit=24)

    if not recent_data:
        context.log.warning("No weather data available for summary")
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(recent_data)

        # Calculate some basic statistics
        if not df.empty:
            avg_temp = df["temperature_f"].mean()
            max_temp = df["temperature_f"].max()
            min_temp = df["temperature_f"].min()
            avg_humidity = df["humidity_percent"].mean()

            context.log.info(f"Summary: Avg Temp: {avg_temp:.1f}°F, "
                           f"Range: {min_temp:.1f}°F - {max_temp:.1f}°F")

            return Output(
                value=df,
                metadata={
                    "record_count": len(df),
                    "avg_temperature_f": round(avg_temp, 2),
                    "max_temperature_f": round(max_temp, 2),
                    "min_temperature_f": round(min_temp, 2),
                    "avg_humidity_percent": round(avg_humidity, 2),
                    "preview": MetadataValue.md(df.head(5).to_markdown())
                }
            )

    return Output(value=df, metadata={"record_count": 0})
