from pydantic import BaseModel


class AddressBase(BaseModel):
    street: str
    number: str
    postal_code: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float


class AddressDisplay(BaseModel):
    street: str
    number: str
    postal_code: str
    city: str
    state: str
    country: str
    latitude: float = None
    longitude: float = None
