from pydantic import BaseModel


class WeatherResponse(BaseModel):
    explanation: str
    current: str
    forecast: list[dict]
