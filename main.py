from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import requests

from models import ApiWeatherData, WeatherData, Response
from db import get_weather_data, update_weather_data
from config import settings

app = FastAPI()


def getWeatherApiUrl(apiKey: str, city: str):
    baseUrl = "https://api.openweathermap.org/data/2.5/weather"
    return f"{baseUrl}?q={city}&appid={apiKey}"


async def getWeatherData(city: str) -> Response:
    # Fetch data from DB
    weather_data = await get_weather_data(city)

    # If data is fresh return
    if weather_data is not None:
        print("INFO: Weather data got from cached data")
        return Response(data=weather_data, error=None)

    url = getWeatherApiUrl(settings.WEATHER_API_KEY, city)
    response = requests.get(url)

    if response.status_code == 200:
        weather = response.json()
        try:
            weather = WeatherData.from_weather_data(ApiWeatherData(**weather))
            weather_data = await update_weather_data(weather)
            return Response(data=weather_data, error=None)
        except ValidationError:
            return Response(data=None, error={"message": "Error while parsing weather data"})
    else:
        return Response(data=None, error={"message": "Error while fetching data"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/weather")
async def read_weather(city: Union[str, None] = None) -> Response:
    if city is None:
        return Response(data=None, error={"message": "City is required"})
    else:
        return await getWeatherData(city)
