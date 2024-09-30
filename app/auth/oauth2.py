from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from app.core import database
from app.services import user
from app.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# TODO SECRET_KEY will be added to environment
# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

SECRET_KEY = "77407c7339a6c00544e51af1101c4abb4aea2a31157ca5f7dfd87da02a628107"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
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


# def can_call_this_api(current_user: UserBase, user_id_in_api_call: int):
#     if (
#         user_id_in_api_call == current_user.id
#         or current_user.user_type == UserType.ADMIN
#     ):
#         return True
#     raise HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="User cannot perform this action",
#     )
