from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate

from app.security import hash_password

def create_user(db: Session, user_data: UserCreate):
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
