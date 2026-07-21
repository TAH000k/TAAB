from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    display_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6)
    birth_year: int
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    birth_year: int
    role: str

    model_config = {
        "from_attributes": True
    }
