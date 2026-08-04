from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.item import Item
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupAddUser, GroupAddItem, GroupResponse
from app.crud import group as group_crud

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.post("", response_model=GroupResponse)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
