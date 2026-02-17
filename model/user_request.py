from pydantic import BaseModel


class UserRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    phone: str
    country: str
    city: str
    password: str
