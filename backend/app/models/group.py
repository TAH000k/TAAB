"""
Group database model and association tables.
Defines the Group model along with junction tables for managing 
many-to-many relationships between groups, users, and items.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Junction table for many-to-many relationship between groups and users
group_users = Table(
    "group_users",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

# Junction table for many-to-many relationship between groups and items
group_items = Table(
    "group_items",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    Column("item_id", Integer, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
)


class Group(Base):
    """
    SQLAlchemy model representing a custom user group.
    Encapsulates group ownership and manages associations with member users and items.
    """
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Many-to-many relationship mappings
    users = relationship("User", secondary=group_users, backref="custom_groups")
    items = relationship("Item", secondary=group_items, backref="assigned_groups")
