from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    category: str | None
    owner_id: int

    class Config:
        from_attributes = True
