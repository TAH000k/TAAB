"""
Authentication and JWT authorization module.
Handles JSON Web Token (JWT) creation, decoding, and dependency-based 
user authentication for FastAPI endpoints.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.user import get_user_by_id


# JWT secret key, algorithm, and lifetime settings
SECRET_KEY = "CHANGE_ME_BEFORE_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# OAuth2 scheme instance pointing to the login endpoint for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)


def create_access_token(data: dict) -> str:
    """
    Generates a new signed JWT access token containing standard payload data and an expiration claim.

    Args:
        data (dict): Payload data to encode within the token (typically includes 'sub').

    Returns:
        str: Encoded JWT string.
    """
    payload = data.copy()

    # Calculate absolute expiration time in UTC
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload["exp"] = expire

    # Sign and encode the token using the secret key
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """
    Decodes and validates a JWT token using the secret key and configured algorithm.

    Args:
        token (str): Encoded JWT string.

    Returns:
        dict | None: Decoded payload dictionary if valid; None if verification fails.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError as e:
        print(e)
        return None
    

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency to authenticate requests using an OAuth2 Bearer token.
    Extracts the user ID from the token payload and fetches the matching user record.

    Args:
        token (str): Injected Bearer token from the authorization header.
        db (Session): Injected database session.

    Returns:
        User: Database model representing the authenticated user.

    Raises:
        HTTPException: 401 UNAUTHORIZED if the token is invalid, missing subject, or user does not exist.
    """
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
        
    user_id = int(user_id)

    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user
