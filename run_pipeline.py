#!/usr/bin/env python3
"""
Simple script to manually run the weather ingestion pipeline.

This is useful for testing and learning how the pipeline works.
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from weather_pipeline.weather_api import WeatherAPIClient
from weather_pipeline.database import WeatherDatabase
from weather_pipeline.config import CITY_NAME


def main():
    """Run the weather ingestion pipeline manually."""
    print(f"Starting weather data ingestion for {CITY_NAME}...")
    print("-" * 50)

    # Step 1: Fetch weather data
    print("\n1. Fetching weather data from API...")
    client = WeatherAPIClient()

    try:
        weather_data = client.fetch_current_weather()
        print(f"   ✓ Successfully fetched weather data")
        print(f"   Temperature: {weather_data['temperature_f']}°F")
        print(f"   Humidity: {weather_data['humidity_percent']}%")
        print(f"   Wind Speed: {weather_data['wind_speed_mph']} mph")
    except Exception as e:
        print(f"   ✗ Error fetching weather data: {e}")
        return 1

    # Step 2: Store in database
    print("\n2. Storing weather data in database...")
    db = WeatherDatabase()

    try:
        row_id = db.insert_weather_data(weather_data)
        if row_id == -1:
            print(f"   ⚠ Duplicate entry (already have data for this timestamp)")
        else:
            print(f"   ✓ Data stored successfully (ID: {row_id})")
    except Exception as e:
        print(f"   ✗ Error storing data: {e}")
        return 1

    # Step 3: Show database stats
    print("\n3. Database Statistics:")
    try:
        stats = db.get_database_stats()
        print(f"   Total records: {stats['total_records']}")
        print(f"   Earliest record: {stats['earliest_record']}")
        print(f"   Latest record: {stats['latest_record']}")
        print(f"   Database size: {stats['database_size_mb']:.2f} MB")
        print(f"   Cities tracked: {', '.join(stats['cities_tracked'])}")
    except Exception as e:
        print(f"   ✗ Error getting stats: {e}")
        return 1

    # Step 4: Show recent observations
    print("\n4. Recent Observations (last 5):")
    try:
        recent = db.get_recent_observations(limit=5)
        for i, obs in enumerate(recent, 1):
            print(f"   {i}. {obs['timestamp']} - {obs['temperature_f']}°F, "
                  f"{obs['humidity_percent']}% humidity")
    except Exception as e:
        print(f"   ✗ Error getting recent observations: {e}")
        return 1

    print("\n" + "-" * 50)
    print("Pipeline completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
