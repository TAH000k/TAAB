from pydantic import BaseModel, Field, ConfigDict

from app.models.user import UserRole


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    display_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    profile_picture: str | None = None
    bio: str | None = None
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
