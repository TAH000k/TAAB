"""
Group API router module.
Provides endpoints for creating user groups, adding members to groups,
and associating items with specific groups.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupAddUser, GroupAddItem, GroupResponse
from app.crud import group as group_crud

# Router configuration for group endpoints
router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post("", response_model=GroupResponse)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new group owned by the current user.

    Args:
        payload (GroupCreate): Group creation payload containing the group name.
        db (Session): Injected database session.
        current_user (User): Authenticated user who will own the group.

    Returns:
        GroupResponse: The created group details including user and item ID lists.
    """
    group = group_crud.create_group(db, name=payload.name, owner_id=current_user.id)
    return GroupResponse(
        id=group.id,
        name=group.name,
        owner_id=group.owner_id,
        user_ids=[u.id for u in group.users],
        item_ids=[i.id for i in group.items]
    )


@router.post("/{group_id}/users", response_model=GroupResponse)
def add_user_to_group(
    group_id: int,
    payload: GroupAddUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Adds a specified user to a group (Group owner action).

    Args:
        group_id (int): ID of the group.
        payload (GroupAddUser): Payload containing the target user_id to add.
        db (Session): Injected database session.
        current_user (User): Authenticated user (must be group owner).

    Returns:
        GroupResponse: Updated group details.

    Raises:
        HTTPException: 404 NOT FOUND if the group or target user does not exist.
    """
    group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user.id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    target_user = db.query(User).filter(User.id == payload.user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_group = group_crud.add_user_to_group(db, group, target_user)
    return GroupResponse(
        id=updated_group.id,
        name=updated_group.name,
        owner_id=updated_group.owner_id,
        user_ids=[u.id for u in updated_group.users],
        item_ids=[i.id for i in updated_group.items]
    )


@router.post("/{group_id}/items", response_model=GroupResponse)
def add_item_to_group(
    group_id: int,
    payload: GroupAddItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Associates an item with a group (Group and Item owner action).

    Args:
        group_id (int): ID of the target group.
        payload (GroupAddItem): Payload containing the item_id to add.
        db (Session): Injected database session.
        current_user (User): Authenticated user (must own both the group and the item).

    Returns:
        GroupResponse: Updated group details.

    Raises:
        HTTPException: 404 NOT FOUND if the group or item does not exist or isn't owned by user.
    """
    group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user.id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    item = db.query(Item).filter(Item.id == payload.item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    updated_group = group_crud.add_item_to_group(db, group, item)
    return GroupResponse(
        id=updated_group.id,
        name=updated_group.name,
        owner_id=updated_group.owner_id,
        user_ids=[u.id for u in updated_group.users],
        item_ids=[i.id for i in updated_group.items]
    )
