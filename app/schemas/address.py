from typing import Optional
from pydantic import BaseModel
from app.models.user import DBUser


class AddressBase(BaseModel):
    street: str
    number: str
    postal_code: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float
    is_address_confirmed: bool = False


class AddressDisplay(BaseModel):
    street: str
    number: str
    postal_code: str
    city: str
    state: str
    country: str
    latitude: float = None
    longitude: float = None
    is_address_confirmed: bool = False

    class Config:
        from_attributes = True


class AddressForm(BaseModel):
    street: Optional[str] = None
    number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_address_confirmed: bool = False

    class Config:
        from_attributes = True


class AddressDisplayPublic(BaseModel):
    city: str
    state: str
    country: str

    class Config:
        from_attributes = True


def create_address_private_display(user: DBUser):
    return AddressDisplay(
        street=user.address.street,
        number=user.address.number,
        postal_code=user.address.postal_code,
        city=user.address.city,
        state=user.address.state,
        country=user.address.country,
        latitude=user.address.latitude,
        longitude=user.address.longitude,
        is_address_confirmed=user.address.is_address_confirmed,
    )


def create_address_public_display(user: DBUser):
    return AddressDisplayPublic(
        city=user.address.city, state=user.address.state, country=user.address.country
    )
