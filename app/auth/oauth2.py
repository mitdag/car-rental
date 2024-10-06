from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.core import database
from app.schemas.enums import UserType
from app.services import user
from app.utils.constants import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# TODO SECRET_KEY will be added to environment
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

SECRET_KEY_ACCESS_TOKEN = (
    "77407c7339a6c00544e51af1101c4abb4aea2a31157ca5f7dfd87da02a628107"
)
SECRET_KEY_REFRESH_TOKEN = (
    "4b3b7fe44b24928b5e686a04733dcda7b8980d202b0e9ada2056982bb8a62496"
)
ALGORITHM = "HS256"


def create_tokens(data: dict):
    to_encode_access_token = data.copy()
    to_encode_refresh_token = data.copy()
    access_token_expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode_access_token.update({"exp": access_token_expire})
    to_encode_refresh_token.update({"exp": refresh_token_expire})
    encoded_access_token_jwt = jwt.encode(
        to_encode_access_token, SECRET_KEY_ACCESS_TOKEN, algorithm=ALGORITHM
    )
    encoded_refresh_token_jwt = jwt.encode(
        to_encode_refresh_token, SECRET_KEY_REFRESH_TOKEN, algorithm=ALGORITHM
    )
    return encoded_access_token_jwt, encoded_refresh_token_jwt


def get_current_user(
    token_enc: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    """
    This function is used for confirming the user with provided access key
    :param token_enc: Access token given to the user during login process.
    :param db: app session
    :return: Current user (DBUser object) if the user is confirmed, raises exception otherwise.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify credentials (credentials might have expired)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = jwt.decode(token_enc, SECRET_KEY_ACCESS_TOKEN, algorithms=ALGORITHM)
        user_email = token.get("username")
        current_user = user.get_user_by_email(user_email, db)
        if not current_user:
            raise Exception()
    except Exception:
        logger.error("Could not authenticate")
        raise credential_exception
    return current_user


def get_current_user_refresh_key(
    refresh_token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    """
    This function is used for confirming the user with provided refresh key during refresh key process.
    :param refresh_token: Refresh token given to the user during login process.
    :param db: app session
    :return: Current user (DBUser object) if the user is confirmed, raises exception otherwise.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not verify credentials (credentials might have expired)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        refresh_token = jwt.decode(
            refresh_token, SECRET_KEY_REFRESH_TOKEN, algorithms=ALGORITHM
        )
        user_email = refresh_token.get("username")
        current_user = user.get_user_by_email(user_email, db)
        if not current_user:
            raise Exception()
    except Exception:
        logger.error("Could not authenticate")
        raise credential_exception
    return current_user, refresh_token


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
