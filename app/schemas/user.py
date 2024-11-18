import time
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.user import DBUser
from app.schemas import address
from app.schemas.address import AddressDisplay, AddressDisplayPublic, AddressUpdate
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
    is_profile_completed: bool = False
    created_at: datetime = time.time()
    last_login: datetime = None


class UserDisplay(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    login_method: Optional[LoginMethod] = LoginMethod.EMAIL
    phone_number: Optional[str] = None
    user_type: Optional[UserType] = UserType.USER
    is_verified: Optional[bool] = False
    is_profile_completed: Optional[bool] = False
    address: Optional[AddressDisplay] = None

    class Config:
        from_attributes = True


class UserProfileFormOld(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    street: Optional[str] = None
    number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileForm(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[AddressUpdate] = None

    class Config:
        from_attributes = True


class UserPublicDisplay(BaseModel):
    id: int
    name: str = None
    last_name: str = None
    address: Optional[AddressDisplayPublic]

    class Config:
        from_attributes = True

