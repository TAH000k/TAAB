"""
Item CRUD operations module.
Provides database access functions for creating, querying, searching,
filtering by visibility/group permissions, and soft-deleting items.
"""

from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.group import Group, group_items, group_users
from app.models.item import Item
from app.schemas.item import ItemCreate


def create_item(
    db: Session,
    item_data: ItemCreate,
    owner_id: int
) -> Item:
    """
    Creates and saves a new item record in the database.

    Args:
        db (Session): Injected database session.
        item_data (ItemCreate): Schema containing the item details.
        owner_id (int): ID of the user creating the item.

    Returns:
        Item: The newly created Item database instance.
    """
    item = Item(
        name=item_data.name,
        description=item_data.description,
        category=item_data.category,
        owner_id=owner_id
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def get_visible_item_by_id(db: Session, item_id: int, observer_id: int) -> Optional[Item]:
    """
    Retrieves a single non-deleted item by ID if it is owned by or shared via a group with the observer.

    Args:
        db (Session): Injected database session.
        item_id (int): ID of the requested item.
        observer_id (int): ID of the user attempting to access the item.

    Returns:
        Optional[Item]: The Item database instance if found and accessible, otherwise None.
    """
    accessible_item_ids = db.query(group_items.c.item_id).join(
        group_users, group_items.c.group_id == group_users.c.group_id
    ).filter(
        group_users.c.user_id == observer_id
    ).scalar_subquery()

    return db.query(Item).filter(
        Item.id == item_id,
        Item.is_deleted == False,
        or_(
            Item.owner_id == observer_id,
            Item.id.in_(accessible_item_ids)
        )
    ).first()


def get_user_items(
    db: Session,
    owner_id: int
) -> List[Item]:
    """
    Retrieves all non-deleted items owned by a specific user.

    Args:
        db (Session): Injected database session.
        owner_id (int): ID of the item owner.

    Returns:
        List[Item]: List of items owned by the specified user.
    """
    return (
        db.query(Item)
        .filter(Item.owner_id == owner_id, Item.is_deleted == False)
        .all()
    )


def search_visible_items(db: Session, query_str: str, observer_id: int) -> List[Item]:
    """
    Searches non-deleted items by matching name or description against a query string,
    filtered by accessibility (owned by or shared with observer).

    Args:
        db (Session): Injected database session.
        query_str (str): Keyword query to match against name or description.
        observer_id (int): ID of the searching user.

    Returns:
        List[Item]: List of unique matching items visible to the observer.
    """
    accessible_item_ids = db.query(group_items.c.item_id).join(
        group_users, group_items.c.group_id == group_users.c.group_id
    ).filter(
        group_users.c.user_id == observer_id
    ).scalar_subquery()

    search_pattern = f"%{query_str}%"

    return db.query(Item).filter(
        Item.is_deleted == False,
        or_(
            Item.name.ilike(search_pattern),
            Item.description.ilike(search_pattern)
        ),
        or_(
            Item.owner_id == observer_id,
            Item.id.in_(accessible_item_ids)
        )
    ).distinct().all()


def get_visible_items_by_user(db: Session, target_user_id: int, observer_id: int) -> List[Item]:
    """
    Retrieves non-deleted items belonging to a target user that are visible to an observer.

    Args:
        db (Session): Injected database session.
        target_user_id (int): ID of the user whose items are requested.
        observer_id (int): ID of the requesting user.

    Returns:
        List[Item]: List of target user's items that are accessible to the observer.
    """
    if target_user_id == observer_id:
        return db.query(Item).filter(
            Item.owner_id == target_user_id,
            Item.is_deleted == False
        ).all()

    return db.query(Item).join(group_items).join(Group).join(group_users).filter(
        Item.owner_id == target_user_id,
        Item.is_deleted == False,
        Group.owner_id == target_user_id,
        group_users.c.user_id == observer_id
    ).distinct().all()


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """
    Retrieves a single non-deleted item by its ID without permission/visibility checks.

    Args:
        db (Session): Injected database session.
        item_id (int): ID of the item.

    Returns:
        Optional[Item]: The Item instance if found and not deleted, otherwise None.
    """
    return db.query(Item).filter(Item.id == item_id, Item.is_deleted == False).first()


def soft_delete_item(db: Session, db_item: Item) -> Item:
    """
    Marks an item as deleted (soft delete) without removing it from the database.

    Args:
        db (Session): Injected database session.
        db_item (Item): The Item database instance to soft delete.

    Returns:
        Item: The updated Item instance with `is_deleted=True`.
    """
    db_item.is_deleted = True
    db.commit()
    db.refresh(db_item)
    return db_item
