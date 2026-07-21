from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(100))

    author: Mapped[str] = mapped_column(String(100))

    description: Mapped[str] = mapped_column(String)

    cover_image: Mapped[str] = mapped_column(String(255))

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    status: Mapped[str] = mapped_column(String(20))

    borrower_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    reserved_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )
