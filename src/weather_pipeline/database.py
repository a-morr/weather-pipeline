"""Database operations for storing weather data in SQLite."""

import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from .config import DATABASE_PATH


class WeatherDatabase:
    """SQLite database for storing weather observations."""

    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_tables_exist()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

    def _ensure_tables_exist(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    city TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    temperature_f REAL,
                    humidity_percent REAL,
                    precipitation_inch REAL,
                    wind_speed_mph REAL,
                    wind_direction_deg REAL,
                    ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(timestamp, city)
                )
            """)

            # Create index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON weather_observations(timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_city
                ON weather_observations(city)
            """)

            conn.commit()

    def insert_weather_data(self, weather_data: Dict[str, Any]) -> int:
        """
        Insert weather observation into database.

        Args:
            weather_data: Dictionary containing weather observation data

        Returns:
            Row ID of inserted record, or -1 if duplicate

        Raises:
            sqlite3.Error: If database operation fails
        """
        with self._get_connection() as conn:
            try:
                cursor = conn.execute("""
                    INSERT INTO weather_observations (
                        timestamp, city, latitude, longitude,
                        temperature_f, humidity_percent, precipitation_inch,
                        wind_speed_mph, wind_direction_deg
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    weather_data["timestamp"],
                    weather_data["city"],
                    weather_data["latitude"],
                    weather_data["longitude"],
                    weather_data["temperature_f"],
                    weather_data["humidity_percent"],
                    weather_data["precipitation_inch"],
                    weather_data["wind_speed_mph"],
                    weather_data["wind_direction_deg"],
                ))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Duplicate entry (same timestamp and city)
                return -1

    def get_recent_observations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent weather observations.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of weather observation dictionaries
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM weather_observations
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_observations_by_city(self, city: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve observations for a specific city.

        Args:
            city: City name
            limit: Maximum number of records to return

        Returns:
            List of weather observation dictionaries
        """
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM weather_observations
                WHERE city = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (city, limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_record_count(self) -> int:
        """Get total number of records in database."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM weather_observations")
            return cursor.fetchone()[0]

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row

            # Total records
            total_records = self.get_record_count()

            # Date range
            cursor = conn.execute("""
                SELECT
                    MIN(timestamp) as earliest,
                    MAX(timestamp) as latest
                FROM weather_observations
            """)
            date_range = dict(cursor.fetchone())

            # Cities tracked
            cursor = conn.execute("""
                SELECT DISTINCT city FROM weather_observations
            """)
            cities = [row[0] for row in cursor.fetchall()]

            return {
                "total_records": total_records,
                "earliest_record": date_range["earliest"],
                "latest_record": date_range["latest"],
                "cities_tracked": cities,
                "database_size_mb": Path(self.db_path).stat().st_size / (1024 * 1024)
                if Path(self.db_path).exists() else 0
            }
