from pydantic import BaseModel


class FlightSearchRequest(BaseModel):
    departure: str
    arrival: str
    outbound_date: str
    return_date: str = ""
    currency: str = "USD"
    travel_class: int = 1
    trip_type: int = 1
    adults: int = 1
    children: int = 0
    infants_in_seat: int = 0
    infants_in_lap: int = 0


class FlightOption(BaseModel):
    departure_time: str
    arrival_time: str
    airlines: str
    duration: str
    layovers: int
    price: str
    carbon_emission: str


class FlightSearchResponse(BaseModel):
    flights: list[FlightOption]
