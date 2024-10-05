from datetime import datetime, timezone
from typing import Optional

from fastapi import Query, HTTPException, status

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.enums import CarEngineType, CarTransmissionType
from app.schemas.user import UserDisplay


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


class CarUpdate(BaseModel):
    make: Optional[str] = None
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


class CarDisplay(BaseModel):
    id: int
    owner: UserDisplay
    make: str
    model: str
    year: int
    transmission_type: CarTransmissionType
    motor_type: CarEngineType
    price_per_day: float
    description: Optional[str]
    is_listed: bool

    class Config:
        from_attributes = True


class RentalPeriod(BaseModel):
    availability_start_date: Optional[datetime] = Field(
        Query(default=None, description="Available cars starting from this day")
    )
    availability_end_date: Optional[datetime] = Field(
        Query(default=None, description="Available cars until this day")
    )

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def validate_dates(cls, values):
        print(datetime.now(timezone.utc))
        start: datetime = values["availability_start_date"]
        end: datetime = values["availability_end_date"]
        if not start and not end:
            return values
        if (start and not end) or (not start and end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both start and end availability dates must be specified",
            )
        if start.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rental must be in the future.",
            )
        if start >= end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be earlier than the end date.",
            )
        return values
