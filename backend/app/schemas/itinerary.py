from pydantic import BaseModel


class ItineraryItem(BaseModel):
    location: str
    time: str


class ItineraryResponse(BaseModel):
    itinerary_by_date: dict[str, list[ItineraryItem]]


class TodoCreate(BaseModel):
    task: str
