from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.enums import CarEngineType, CarMake, CarTransmissionType
from app.schemas.review import ReviewDisplay
from app.schemas.user import UserPublicDisplay


def validate_year(value: int) -> int:
    current_year = datetime.now().year + 1
    if value > current_year:
        raise ValueError(
            f"Year cannot be in the future. Current year is {current_year}."
        )
    if value < 1900:
        raise ValueError("Year cannot be earlier than 1900")
    return value


class CarBase(BaseModel):
    owner_id: int
    make: str
    model: str
    year: int = Field(default=datetime.utcnow().year)
    transmission_type: CarTransmissionType
    motor_type: CarEngineType
    price_per_day: float
    description: Optional[str] = None
    is_listed: bool = True

    @field_validator("year")
    def validate_year_field(cls, value):
        return validate_year(value)

    class Config:
        from_attributes = True


class CarCreate(BaseModel):
    make: CarMake
    model: str
    year: int = Field(default=datetime.utcnow().year)
    transmission_type: CarTransmissionType
    motor_type: CarEngineType
    price_per_day: float
    description: Optional[str] = None
    is_listed: bool = True

    @field_validator("year")
    def validate_year_field(cls, value):
        return validate_year(value)

    class Config:
        from_attributes = True


class CarUpdate(BaseModel):
    make: Optional[CarMake] = None
    model: Optional[str] = None
    year: Optional[int] = Field(default=datetime.utcnow().year)
    transmission_type: Optional[CarTransmissionType] = None
    motor_type: Optional[CarEngineType] = None
    price_per_day: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    is_listed: Optional[bool] = None

    @field_validator("year")
    def validate_year_field(cls, value):
        if value is not None:  # Optional validation
            return validate_year(value)
        return value

    class Config:
        from_attributes = True


class CarRentalDisplay(BaseModel):
    id: Optional[int]
    renter_id: Optional[int]
    total_price: Optional[float]
    reviews: Optional[List[ReviewDisplay]]

    class Config:
        from_attributes = True


class CarDisplay(BaseModel):
    id: Optional[int]
    owner: Optional[UserPublicDisplay]
    make: Optional[str]
    model: Optional[str]
    year: Optional[int]
    transmission_type: Optional[CarTransmissionType]
    motor_type: Optional[CarEngineType]
    price_per_day: Optional[float]
    description: Optional[str]
    is_listed: Optional[bool]
    rentals: Optional[List[CarRentalDisplay]]

    class Config:
        from_attributes = True
