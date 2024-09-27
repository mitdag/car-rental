from datetime import datetime
import time
from pydantic import BaseModel

from app.schemas.enums import LoginMethod, UserType


class UserBase(BaseModel):
    id: int
    name: str = None
    last_name: str = None
    email: str
    password: str = None
    login_method: LoginMethod
    phone_number: str = None
    user_type: UserType
    is_verified: bool = False
    created_at: datetime = time.time()
    last_login: datetime = None


class UserDisplay(BaseModel):
    id: int
    name: str = None
    last_name: str = None
    email: str
    login_method: LoginMethod
    phone_number: str = None
    user_type: UserType
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    id: int
    name: str
    last_name: str
    phone_number: str
    street: str
    number: str
    postal_code: str
    city: str
    state: str
    country: str

    class Config:
        from_attributes = True
