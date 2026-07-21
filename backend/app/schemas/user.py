from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    display_name: str
    password: str
    birth_year: int
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
