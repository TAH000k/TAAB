from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate

from app.security import hash_password, verify_password


def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        username=user_data.username,
        display_name=user_data.display_name,
        password_hash=hash_password(user_data.password),
        birth_year=user_data.birth_year,
        role=user_data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
