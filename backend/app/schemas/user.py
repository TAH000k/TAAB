"""
Pydantic schemas for user management.
Defines data validation models for user creation requests and
structured user response data.
"""

from pydantic import BaseModel, Field, ConfigDict

from app.models.user import UserRole


class UserCreate(BaseModel):
    """
    Schema for user registration and creation request payload validation.
    """
    username: str = Field(min_length=3, max_length=32)
    display_name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    """
    Response model representing public user profile details and account role.
    """
    id: int
    username: str
    display_name: str
    profile_picture: str | None = None
    bio: str | None = None
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
