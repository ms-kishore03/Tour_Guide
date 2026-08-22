from pydantic import BaseModel


class AttractionsResponse(BaseModel):
    status: str
    places: list[str]


class GeoResponse(BaseModel):
    lat: float | None
    lon: float | None
    raw: list[str]
