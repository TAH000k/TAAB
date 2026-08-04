from pydantic import BaseModel, ConfigDict
from typing import List

class GroupCreate(BaseModel):
    name: str

class GroupAddUser(BaseModel):
    user_id: int

class GroupAddItem(BaseModel):
    item_id: int

class GroupResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    user_ids: List[int] = []
    item_ids: List[int] = []

    model_config = ConfigDict(from_attributes=True)
