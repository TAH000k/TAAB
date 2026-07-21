from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(32), unique=True)

    display_name: Mapped[str] = mapped_column(String(50))

    password_hash: Mapped[str] = mapped_column(String(255))

    birth_year: Mapped[int] = mapped_column(Integer)

    role: Mapped[str] = mapped_column(String(20))
