from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.core import database
from app.schemas.enums import UserType
from app.services import user
from app.utils.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# TODO SECRET_KEY will be added to environment
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

SECRET_KEY = "77407c7339a6c00544e51af1101c4abb4aea2a31157ca5f7dfd87da02a628107"
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token_enc: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify credentials (credentials might have expired)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = jwt.decode(token_enc, SECRET_KEY, algorithms=ALGORITHM)
        user_email = token.get("username")
        current_user = user.get_user_by_email(user_email, db)
        if not current_user:
            raise Exception()
    except Exception:
        logger.error("Could not authenticate")
        raise credential_exception
    return current_user


def admin_only(
    current_user=Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """
    Dependency that restricts access to admin users only.

    This function checks if the current user has admin privileges. If the user is not an admin,
    it raises an HTTP 403 Forbidden exception. If the user is an admin, it returns the user object.

    Args:
        current_user: A dependency that retrieves the currently authenticated user.
        db: A dependency that provides the database session.

    Raises:
        HTTPException: If the user does not have admin privileges, an exception with status code 403 is raised.

    Returns:
        user: The current user object if they have admin privileges.
    """
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required.",
        )
    return current_user


def complete_user_profile_only(
    current_user=Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    """
    Dependency that restricts access to users with complete profiles only.

    This function checks if the current user has a complete profile. If the profile is not complete,
    it raises an HTTP 403 Forbidden exception. If the profile is complete, it returns the user object.

    Args:
        current_user: A dependency that retrieves the currently authenticated user.
        db: A dependency that provides the database session.

    Raises:
        HTTPException: If the user's profile is not complete, an exception with status code 403 is raised.
    """
    # Check if the user's profile is complete
    is_complete = user.is_user_profile_complete(current_user.id, db)

    if not is_complete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Please complete your profile before accessing this resource.",
        )

    return current_user
