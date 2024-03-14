from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ApiWeatherSys(BaseModel):
    country: str


class ApiWeatherMain(BaseModel):
    temp: float
    feels_like: float
    pressure: int
    humidity: int


class ApiWeatherWind(BaseModel):
    speed: float


class ApiWeather(BaseModel):
    main: str
    description: str
    icon: str


class ApiWeatherData(BaseModel):
    name: str
    sys: ApiWeatherSys
    main: ApiWeatherMain
    wind: ApiWeatherWind
    weather: list[ApiWeather]


class WeatherData(BaseModel):
    id: Optional[int]
    city: str
    country: str
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    wind_speed: float
    description: str
    icon: str
    updated_at: Optional[datetime]

    @classmethod
    def from_tuple(cls, tpl: tuple):
        return cls(**{k: v for k, v in zip(cls.__fields__.keys(), tpl)})

    @classmethod
    def from_weather_data(cls, data: ApiWeatherData):
        return cls(
            id=None,
            city=data.name,
            country=data.sys.country,
            temp=data.main.temp,
            feels_like=data.main.feels_like,
            pressure=data.main.pressure,
            humidity=data.main.humidity,
            wind_speed=data.wind.speed,
            description=data.weather[0].description,
            icon=data.weather[0].icon,
            updated_at=datetime.now(),
        )


class Response(BaseModel):
    data: Optional[WeatherData]
    error: Optional[dict]
