from pydantic import BaseModel


class SaveTripRequest(BaseModel):
    place_name: str
    scenario: str
    climate: str
    duration: str
    people: str
    transport: str
    description: str

    def to_legacy_dict(self) -> dict:
        return {
            "Place Name": self.place_name,
            "Scenario": self.scenario,
            "Climate": self.climate,
            "Duration": self.duration,
            "People": self.people,
            "Transport": self.transport,
            "Description": self.description,
        }


class TripResponse(BaseModel):
    place_name: str
    scenario: str
    climate: str
    duration: str
    people: str
    transport: str
    description: str

    @classmethod
    def from_legacy_dict(cls, data: dict) -> "TripResponse":
        return cls(
            place_name=data.get("Place Name", ""),
            scenario=data.get("Scenario", ""),
            climate=data.get("Climate", ""),
            duration=data.get("Duration", ""),
            people=data.get("People", ""),
            transport=data.get("Transport", ""),
            description=data.get("Description", ""),
        )


class MessageResponse(BaseModel):
    message: str


class ExploreRequest(BaseModel):
    trip_theme: str
    activity: str
    climate: str
    budget: str
    duration: str
    location: str
    trip_type: str
    transport: str


class ExploreSuggestion(BaseModel):
    name: str
    description: str


class ExploreResponse(BaseModel):
    places: list[ExploreSuggestion]
