from typing import Dict, Optional

from pydantic import BaseModel, model_validator

from app.models.user import DBUser
from app.utils.address_translation import AddressValidationError, address_to_lat_lon
from app.utils.logger import logger


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
    street: Optional[str] = None
    number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_address_confirmed: Optional[bool] = False

    class Config:
        from_attributes = True


# Function that validates an address and adds latitude/longitude
def validate_address(values: Dict) -> Dict:
    street = values.get("street")
    number = values.get("number")
    postal_code = values.get("postal_code")
    city = values.get("city")
    state = values.get("state")
    country = values.get("country")

    # Build the address dictionary for geocoding
    address_dict = {
        "street": f"{street} {number}" if street and number else None,
        "postalcode": postal_code,
        "city": city,
        "state": state,
        "country": country,
    }

    # Remove None values from the dictionary
    address_dict = {k: v for k, v in address_dict.items() if v}

    if address_dict:
        try:
            # Validate address through geocoding
            lat_lon = address_to_lat_lon(address_dict)
            logger.info(f"Address geocoded successfully: {lat_lon}")
            # Add latitude and longitude to the validated data
            values["latitude"] = lat_lon["latitude"]
            values["longitude"] = lat_lon["longitude"]
        except AddressValidationError as e:
            raise ValueError(f"Address validation failed: {e}")

    return values


class AddressForm(BaseModel):
    street: Optional[str] = None
    number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_address_confirmed: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True

    # Validator to check and validate the address by geocoding
    @model_validator(mode="before")
    def validate_address(cls, values):
        return validate_address(values)


class AddressUpdate(BaseModel):
    street: Optional[str] = None
    number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True

    # Validator to check and validate the address by geocoding
    @model_validator(mode="before")
    def validate_address(cls, values):
        return validate_address(values)


class AddressDisplayPublic(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

    class Config:
        from_attributes = True


def create_address_private_display(user: DBUser):
    if not user or not user.address:
        return None
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
    if not user or not user.address:
        return None
    return AddressDisplayPublic(
        city=user.address.city, state=user.address.state, country=user.address.country
    )
