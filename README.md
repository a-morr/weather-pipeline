# Weather Data Ingestion Pipeline

A batch process data ingestion pipeline built with **Dagster** that fetches weather data from a free API and stores it locally in SQLite. Perfect for learning data engineering concepts!

## What You'll Learn

- **Dagster**: Building data pipelines with assets, jobs, and schedules
- **Python API Integration**: Making HTTP requests to external APIs
- **SQLite Database**: Storing and querying structured data
- **Batch Processing**: Running periodic data ingestion tasks
- **Data Orchestration**: Scheduling and monitoring pipeline runs

## Features

- Fetches current weather data from Open-Meteo (free, no API key required!)
- Stores data in a local SQLite database
- Dagster UI for monitoring pipeline runs
- Scheduled jobs (hourly or every 15 minutes)
- Data quality checks and statistics
- Fully local - no cloud services needed

## Project Structure

```
weather-pipeline/
├── src/weather_pipeline/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── weather_api.py      # API client for fetching weather data
│   ├── database.py         # SQLite database operations
│   ├── assets.py           # Dagster assets (pipeline steps)
│   ├── definitions.py      # Dagster jobs and schedules
│   └── sensors.py          # Event-driven triggers
├── data/                   # SQLite database stored here
├── run_pipeline.py         # Manual pipeline execution script
├── requirements.txt        # Python dependencies
└── .env                    # Configuration (you'll create this)
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### 2. Install Dependencies

```bash
cd weather-pipeline

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Your Location

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` to set your location:

```bash
# Change these to your city's coordinates
LATITUDE=40.7128
LONGITUDE=-74.0060
CITY_NAME=New_York
```

To find your coordinates, search "[your city] coordinates" on Google.

## Running the Pipeline

### Option 1: Manual Run (Great for Testing)

Run the pipeline once to test it:

```bash
python run_pipeline.py
```

This will:
1. Fetch current weather data
2. Store it in the database
3. Show statistics and recent observations

### Option 2: Dagster UI (Full Experience)

Start the Dagster web interface:

```bash
cd weather-pipeline
DAGSTER_HOME=. dagster dev -m src.weather_pipeline.definitions
```

Then open your browser to: http://localhost:3000

#### What You Can Do in Dagster UI:

1. **View Assets**: See your data pipeline as a graph
2. **Materialize Assets**: Click "Materialize all" to run the pipeline
3. **View Runs**: See history of all pipeline executions
4. **Enable Schedules**: Turn on automatic hourly runs
5. **See Metadata**: View temperature, humidity, and database stats

### Option 3: Command Line with Dagster

Run the pipeline from command line:

```bash
DAGSTER_HOME=. dagster asset materialize -m src.weather_pipeline.definitions --select "*"
```

## Understanding the Pipeline

### Assets (Pipeline Steps)

1. **raw_weather_data**: Fetches weather from Open-Meteo API
2. **stored_weather_data**: Saves data to SQLite database
3. **weather_summary**: Generates statistics from recent data

### Schedules

- **hourly_weather_schedule**: Runs every hour (production)
- **frequent_weather_schedule**: Runs every 15 minutes (testing)

To enable a schedule in Dagster UI:
1. Go to "Schedules" tab
2. Toggle the schedule on
3. Watch it run automatically!

## Learning Activities

### Beginner Tasks

1. Run the manual script 3-4 times and watch the database grow
2. Open the Dagster UI and materialize the assets manually
3. Check the database: `sqlite3 data/weather.db "SELECT * FROM weather_observations;"`
4. Modify the city coordinates in `.env` to track a different location

### Intermediate Tasks

1. Enable the hourly schedule and let it run for a day
2. Add a new weather metric (like cloud cover or visibility)
3. Create a new asset that calculates daily averages
4. Add email or Slack notifications for extreme temperatures

### Advanced Tasks

1. Track multiple cities simultaneously
2. Add data validation (reject obviously wrong values)
3. Create a sensor that triggers on temperature changes
4. Export data to CSV for analysis in Excel/Pandas
5. Add weather forecast ingestion (7-day forecast)

## Database Schema

```sql
weather_observations
  - id (PRIMARY KEY)
  - timestamp
  - city
  - latitude, longitude
  - temperature_f
  - humidity_percent
  - precipitation_inch
  - wind_speed_mph
  - wind_direction_deg
  - ingestion_time
```

## Viewing Your Data

### Using SQLite Command Line

```bash
# Open database
sqlite3 data/weather.db

# View all data
SELECT * FROM weather_observations;

# Get latest reading
SELECT * FROM weather_observations ORDER BY timestamp DESC LIMIT 1;

# Get average temperature for today
SELECT AVG(temperature_f) FROM weather_observations
WHERE DATE(timestamp) = DATE('now');

# Exit sqlite
.quit
```

### Using Python

```python
from weather_pipeline.database import WeatherDatabase

db = WeatherDatabase()

# Get recent observations
recent = db.get_recent_observations(limit=10)
for obs in recent:
    print(f"{obs['timestamp']}: {obs['temperature_f']}°F")

# Get statistics
stats = db.get_database_stats()
print(stats)
```

## API Information

This project uses **Open-Meteo**, a free weather API:
- No API key required
- No rate limits for reasonable use
- Data updated hourly
- Documentation: https://open-meteo.com/

## Troubleshooting

### "Module not found" error
Make sure you're in the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Database is locked" error
Close any other programs accessing the database file.

### API timeout
Check your internet connection. The API might be temporarily unavailable.

### Dagster UI won't start
Make sure port 3000 isn't already in use. Try a different port:
```bash
DAGSTER_HOME=. dagster dev -m src.weather_pipeline.definitions -p 3001
```

## Cost

- **Total cost: $0** (completely free!)
- Uses free Open-Meteo API
- Runs entirely on your local computer
- SQLite database is free and lightweight

## Next Steps

After mastering this pipeline, you can:
- Add more data sources (stock prices, news, etc.)
- Deploy to a server for 24/7 operation
- Add data visualization with Plotly or Matplotlib
- Integrate with dbt for data transformations
- Connect to cloud storage (S3, BigQuery, etc.)

## Resources

- [Dagster Documentation](https://docs.dagster.io/)
- [Open-Meteo API Docs](https://open-meteo.com/en/docs)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Python Requests Library](https://requests.readthedocs.io/)

## License

This is a learning project - feel free to modify and use it however you like!
