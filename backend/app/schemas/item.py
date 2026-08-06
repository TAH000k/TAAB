"""
Pydantic schemas for item operations.
Defines data models for creating items and returning item details,
including computed availability fields.
"""

from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    """
    Schema for creating a new item listing.
    """
    name: str
    description: str | None = None
    category: str | None = None


class ItemResponse(BaseModel):
    """
    Response model representing item details along with availability status.
    """
    id: int
    owner_id: int
    name: str
    description: str | None
    category: str | None
    image_url: str | None

    # Status indicators dynamically set during serialization
    available: bool
    current_borrow_id: int | None

    model_config = ConfigDict(from_attributes=True)
