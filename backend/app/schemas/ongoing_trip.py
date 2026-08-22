from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class OngoingTripResponse(BaseModel):
    username: str
    place: str
    trip_details: dict = {}
    expenses: list[dict] = []


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: str


class ExpenseResponse(BaseModel):
    amount: float
    category: str
    date: str
