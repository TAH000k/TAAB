from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.item import ItemCreate, ItemResponse
from app.crud import item as item_crud
from app.models.user import User
from app.auth import get_current_user


router = APIRouter(
    prefix="/items",
    tags=["Items"]
)


@router.post("/", response_model=ItemResponse)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return item_crud.create_item(
        db,
        item,
        current_user.id
    )


@router.get("/me", response_model=list[ItemResponse])
def get_my_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return item_crud.get_user_items(
        db,
        current_user.id
    )


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = item_crud.get_item(
        db,
        item_id
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = item_crud.get_item(
        db,
        item_id
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not your item"
        )

    item_crud.delete_item(
        db,
        item
    )

    return {
        "message": "Item deleted"
    }
