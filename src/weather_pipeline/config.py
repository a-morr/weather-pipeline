"""Configuration management for the weather pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Weather API configuration
LATITUDE = float(os.getenv("LATITUDE", "40.4255"))
LONGITUDE = float(os.getenv("LONGITUDE", "-111.7945"))
CITY_NAME = os.getenv("CITY_NAME", "Highland")

# Database configuration
DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    str(PROJECT_ROOT / "data" / "weather.db")
)

# API endpoint for Open-Meteo (free weather API)
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Ensure data directory exists
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
