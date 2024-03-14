import psycopg2
import atexit
from datetime import datetime, timedelta
from typing import Optional

from models import WeatherData
from config import settings


conn = psycopg2.connect(database=settings.DB_NAME,
                        host=settings.DB_HOST,
                        user=settings.DB_USER,
                        password=settings.DB_PASSWORD,
                        port=settings.DB_PORT)


async def insert_weather_data(data: WeatherData) -> Optional[WeatherData]:
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO 
            "WeatherData" (city, country, temp, feels_like, pressure, humidity, wind_speed, description, icon) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
                       (data.city, data.country, data.temp, data.feels_like, data.pressure, data.humidity, data.wind_speed, data.description, data.icon))
        conn.commit()
        new_data = cursor.fetchone()
        if new_data is not None:
            new_data = WeatherData.from_tuple(new_data)
        cursor.close()

        return new_data
    except Exception as e:
        print("insert error", e)
        conn.rollback()
        return None


async def update_weather_data(data: WeatherData) -> Optional[WeatherData]:
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE "WeatherData" SET temp = %s, feels_like = %s, pressure = %s, humidity = %s, wind_speed = %s, description = %s, icon = %s, updated_at = %s WHERE city = %s
            RETURNING *
            """,
                       (data.temp, data.feels_like, data.pressure, data.humidity, data.wind_speed, data.description, data.icon, data.updated_at, data.city))

        conn.commit()
        updated_data = cursor.fetchone()
        if updated_data is None:
            updated_data = await insert_weather_data(data)
        else:
            updated_data = WeatherData.from_tuple(updated_data)
        cursor.close()

        return updated_data
    except Exception as e:
        print("update error", e)
        conn.rollback()
        return None


async def get_weather_data(city: str) -> Optional[WeatherData]:
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM "WeatherData" WHERE city = %s and updated_at >= %s
            """,
                       (city, datetime.now() - timedelta(seconds=10)))
        data = cursor.fetchone()

        if data is not None:
            data = WeatherData.from_tuple(data)

        cursor.close()
        return data
    except Exception as e:
        print("get error", e)
        conn.rollback()
        return None


def close_connection():
    conn.close()
    print("INFO: Database connection closed")


atexit.register(close_connection)
