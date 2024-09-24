from datetime import datetime
import time
from pydantic import BaseModel

from app.schemas.enums import LoginMethod, UserType


class UserBase(BaseModel):
    name: str = None
    last_name: str = None
    email: str
    password: str = None
    login_method: LoginMethod
    phone_number: str = None
    address_lat: float = None
    address_lon: float = None
    user_type: UserType
    is_verified: bool = False
    created_at: datetime = time.time()
    last_login: datetime = None


class UserDisplay(BaseModel):
    name: str = None
    last_name: str = None
    email: str
    login_method: LoginMethod
    phone_number: str = None
    user_type: UserType
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserProfile(BaseModel):
    user_id: int
    name: str
    last_name: str
    phone_number: str
    street: str
    number: str
    postal_code: str
    city: str
    state: str
    country: str
