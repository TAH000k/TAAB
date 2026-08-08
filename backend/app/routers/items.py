"""
Item API router module.
Provides endpoints for creating, retrieving, searching, updating media,
and deleting items with visibility and authorization checks.
"""

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import os
from pathlib import Path

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.schemas.item import ItemCreate, ItemResponse
from app.crud import item as item_crud
from app.services.item import serialize_item, serialize_items
from app.services.media import save_uploaded_file

# Router configuration for item endpoints
router = APIRouter(
    prefix="/items",
    tags=["Items"],
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def delete_old_file_if_exists(file_path: str):
    if not file_path or file_path == "/static/defaults/ditempic.webp":
        return

    clean_relative_path = file_path.lstrip("/")

    full_path = (BASE_DIR / clean_relative_path).resolve()

    if full_path.exists() and full_path.is_file():
        os.remove(full_path)


@router.post(
    "/",
    response_model=ItemResponse,
)
def create_item(
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new item listing for the authenticated user.

    Args:
        item_data (ItemCreate): Payload containing item details.
        db (Session): Injected database session.
        current_user (User): Authenticated user who owns the new item.

    Returns:
        ItemResponse: Serialized item details including availability status.
    """
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
def search_items(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Searches for visible items matching a query string.

    Args:
        q (str): Search query keyword.
        db (Session): Injected database session.
        current_user (User): Authenticated user performing the search.

    Returns:
        List[ItemResponse]: List of matching serialized items visible to the user.
    """
    items = item_crud.search_visible_items(db, query_str=q, observer_id=current_user.id)
    return [serialize_item(db, item) for item in items]


@router.post("/{item_id}/upload-image")
def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads and attaches an image file to a specific item.

    Args:
        item_id (int): ID of the item.
        file (UploadFile): Uploaded image file.
        db (Session): Injected database session.
        current_user (User): Authenticated user (must be item owner).

    Returns:
        dict: Object containing the generated relative image URL.

    Raises:
        HTTPException: 404 NOT FOUND if the item does not exist.
        HTTPException: 403 FORBIDDEN if the user is not the item owner.
    """
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

    delete_old_file_if_exists(db_item.image_url)
    
    image_url = save_uploaded_file(file, folder="items")
    db_item.image_url = image_url
    db.commit()
    db.refresh(db_item)

    return {"image_url": image_url}


@router.post("/{item_id}/reset-image")
def upload_item_image(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads and attaches an image file to a specific item.

    Args:
        item_id (int): ID of the item.
        db (Session): Injected database session.
        current_user (User): Authenticated user (must be item owner).

    Returns:
        dict: Object containing the generated relative image URL.

    Raises:
        HTTPException: 404 NOT FOUND if the item does not exist.
        HTTPException: 403 FORBIDDEN if the user is not the item owner.
    """
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

    delete_old_file_if_exists(db_item.image_url)
    
    image_url = "/static/defaults/ditempic.webp"
    db_item.image_url = image_url
    db.commit()
    db.refresh(db_item)

    return {"image_url": image_url}


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves details for a single visible item by its ID.

    Args:
        item_id (int): ID of the item.
        db (Session): Injected database session.
        current_user (User): Authenticated requesting user.

    Returns:
        ItemResponse: Serialized item details.

    Raises:
        HTTPException: 404 NOT FOUND if the item does not exist or is not visible.
    """
    item = item_crud.get_visible_item_by_id(db, item_id=item_id, observer_id=current_user.id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return serialize_item(db, item)


@router.get(
    "/",
    response_model=list[ItemResponse],
)
def get_my_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves all items owned by the currently authenticated user.

    Args:
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        list[ItemResponse]: Batch-serialized list of the user's items.
    """
    items = item_crud.get_user_items(
        db=db,
        owner_id=current_user.id,
    )

    return serialize_items(
        db,
        items,
    )


@router.get("/user/{target_user_id}", response_model=List[ItemResponse])
def get_user_visible_items(
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves items belonging to a target user that are visible to the requesting user.

    Args:
        target_user_id (int): ID of the item owner whose items are requested.
        db (Session): Injected database session.
        current_user (User): Authenticated requesting user.

    Returns:
        List[ItemResponse]: List of visible serialized items.
    """
    items = item_crud.get_visible_items_by_user(
        db,
        target_user_id=target_user_id,
        observer_id=current_user.id
    )
    return [serialize_item(db, item) for item in items]


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft-deletes an item owned by the authenticated user.

    Args:
        item_id (int): ID of the item to delete.
        db (Session): Injected database session.
        current_user (User): Authenticated user (must be item owner).

    Returns:
        dict: Confirmation message on success.

    Raises:
        HTTPException: 404 NOT FOUND if item does not exist or user is not owner.
    """
    db_item = item_crud.get_item(db, item_id=item_id)

    if not db_item or db_item.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    item_crud.soft_delete_item(db, db_item=db_item)
    return {"message": "Item deleted successfully"}
