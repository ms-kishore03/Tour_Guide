from pydantic import BaseModel


class UserContext(BaseModel):
    username: str
    email: str
