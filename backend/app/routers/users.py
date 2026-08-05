from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import create_user , get_user_by_username
from app.models.user import User
from app.services.media import save_uploaded_file
from app.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=UserResponse)
def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    return create_user(db, user)


@router.post("/upload-profile_picture")
def upload_user_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_user = get_user_by_username(db, username=current_user.username)

    profile_picture = save_uploaded_file(file, folder="users")
    db_user.profile_picture = profile_picture
    db.commit()
    db.refresh(db_user)

    return {"profile_picture": profile_picture}
