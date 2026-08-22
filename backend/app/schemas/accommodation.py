from pydantic import BaseModel


class AccommodationSearchRequest(BaseModel):
    location: str
    checkin: str
    checkout: str


class AccommodationSearchResponse(BaseModel):
    results: list[str]
