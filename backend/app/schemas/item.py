from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None


class ItemResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str | None
    category: str | None
    image: str | None

    available: bool
    current_borrow_id: int | None

    model_config = ConfigDict(from_attributes=True)
