"""
Pydantic schemas for group management.
Defines request and response models for creating groups, adding members or items,
and serving structured group details.
"""

from typing import List
from pydantic import BaseModel, ConfigDict


class GroupCreate(BaseModel):
    """
    Schema for creating a new group.
    """
    name: str


class GroupAddUser(BaseModel):
    """
    Schema for adding a user to an existing group.
    """
    user_id: int


class GroupAddItem(BaseModel):
    """
    Schema for associating an item with a group.
    """
    item_id: int


class GroupResponse(BaseModel):
    """
    Response model representing detailed group information,
    including associated user and item identifiers.
    """
    id: int
    name: str
    owner_id: int
    user_ids: List[int] = []
    item_ids: List[int] = []

    model_config = ConfigDict(from_attributes=True)
