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
        owner_id=owner_id,
        image_url="/static/defaults/ditempic.webp"
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
    owner_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[Item]:
    """
    Retrieves all non-deleted items owned by a specific user with pagination.
    """
    return (
        db.query(Item)
        .filter(Item.owner_id == owner_id, Item.is_deleted == False)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_visible_items(
    db: Session, 
    observer_id: int,
    skip: int = 0,
    limit: int = 20,
    search_query: Optional[str] = None,
    category: Optional[str] = None,
    is_available: Optional[bool] = None
) -> List[Item]:
    """
    Retrieves visible items (owned by or shared with observer) with support 
    for pagination, searching, and filtering.

    Args:
        db (Session): Injected database session.
        observer_id (int): ID of the searching user.
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        search_query (Optional[str]): Keyword query to match against name or description.
        category (Optional[str]): Filter by item category.
        is_available (Optional[bool]): Filter by availability status.

    Returns:
        List[Item]: List of matching items visible to the observer.
    """
    accessible_item_ids = db.query(group_items.c.item_id).join(
        group_users, group_items.c.group_id == group_users.c.group_id
    ).filter(
        group_users.c.user_id == observer_id
    ).scalar_subquery()

    query = db.query(Item).filter(
        Item.is_deleted == False,
        or_(
            Item.owner_id == observer_id,
            Item.id.in_(accessible_item_ids)
        )
    )

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Item.name.ilike(search_pattern),
                Item.description.ilike(search_pattern)
            )
        )

    if category:
        query = query.filter(Item.category == category)

    if is_available is not None:
        query = query.filter(Item.is_available == is_available)

    return query.distinct().offset(skip).limit(limit).all()


def get_visible_items_by_user(
    db: Session, 
    target_user_id: int, 
    observer_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[Item]:
    """
    Retrieves non-deleted items belonging to a target user that are visible to an observer (Paginated).
    """
    if target_user_id == observer_id:
        return db.query(Item).filter(
            Item.owner_id == target_user_id,
            Item.is_deleted == False
        ).offset(skip).limit(limit).all()

    return db.query(Item).join(group_items).join(Group).join(group_users).filter(
        Item.owner_id == target_user_id,
        Item.is_deleted == False,
        Group.owner_id == target_user_id,
        group_users.c.user_id == observer_id
    ).distinct().offset(skip).limit(limit).all()


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
