"""Weather API client for fetching data from Open-Meteo."""

import requests
from datetime import datetime
from typing import Dict, Any
from .config import WEATHER_API_URL, LATITUDE, LONGITUDE, CITY_NAME


class WeatherAPIClient:
    """Client for interacting with Open-Meteo weather API."""

    def __init__(self, latitude: float = LATITUDE, longitude: float = LONGITUDE):
        """
        Initialize the weather API client.

        Args:
            latitude: Latitude coordinate for weather location
            longitude: Longitude coordinate for weather location
        """
        self.latitude = latitude
        self.longitude = longitude
        self.api_url = WEATHER_API_URL

    def fetch_current_weather(self) -> Dict[str, Any]:
        """
        Fetch current weather data from the API.

        Returns:
            Dictionary containing weather data

        Raises:
            requests.RequestException: If API request fails
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "wind_direction_10m"
            ],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch"
        }

        response = requests.get(self.api_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract current weather data
        current = data.get("current", {})

        return {
            "timestamp": datetime.fromisoformat(current.get("time")),
            "city": CITY_NAME,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "temperature_f": current.get("temperature_2m"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "precipitation_inch": current.get("precipitation"),
            "wind_speed_mph": current.get("wind_speed_10m"),
            "wind_direction_deg": current.get("wind_direction_10m"),
        }

    def fetch_daily_forecast(self, days: int = 7) -> Dict[str, Any]:
        """
        Fetch daily weather forecast.

        Args:
            days: Number of forecast days (max 16)

        Returns:
            Dictionary containing forecast data
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "wind_speed_10m_max"
            ],
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "forecast_days": days
        }

        response = requests.get(self.api_url, params=params, timeout=10)
        response.raise_for_status()

        return response.json()
