from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.schemas.item import ItemCreate, ItemResponse
from app.crud import item as item_crud
from app.services.item import serialize_item, serialize_items
from app.services.media import save_uploaded_file

from typing import List

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)


@router.post(
    "/",
    response_model=ItemResponse,
)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = item_crud.create_item(
        db=db,
        item_data=item_data,
        owner_id=current_user.id,
    )

    return serialize_item(
        db,
        item,
    )
    

@router.get("/search", response_model=List[ItemResponse])
def search_items_endpoint(
    q: str,
    db: Session = Depends(get_db)
):
    items = item_crud.search_items(db, q=q)
    return [serialize_item(db, item) for item in items]

    
@router.post("/{item_id}/upload-image")
def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = item_crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    if db_item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )

    image_url = save_uploaded_file(file, folder="items")
    db_item.image_url = image_url
    db.commit()
    db.refresh(db_item)

    return {"image_url": image_url}


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = item_crud.get_item(
        db=db,
        item_id=item_id,
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
        )

    return serialize_item(
        db,
        item,
    )


@router.get(
    "/",
    response_model=list[ItemResponse],
)
def get_my_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = item_crud.get_user_items(
        db=db,
        owner_id=current_user.id,
    )

    return serialize_items(
        db,
        items,
    )


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = item_crud.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    if db_item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )

    item_crud.delete_item(db, item=db_item)

    return {"message": "Item deleted successfully"}
