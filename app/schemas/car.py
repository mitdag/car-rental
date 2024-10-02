from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserDisplay


class CarBase(BaseModel):
    owner_id: int
    make: str
    model: str
    year: int
    transmission_type: str
    motor_type: str
    price_per_day: float
    description: Optional[str] = None
    is_listed: bool = True


class CarCreate(BaseModel):
    make: str
    model: str
    year: int
    transmission_type: str
    motor_type: str
    price_per_day: float
    description: Optional[str] = None
    is_listed: bool = True

    class Config:
        from_attributes = True


class CarUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = Field(None, ge=1900, le=2025)
    transmission_type: Optional[str] = None
    motor_type: Optional[str] = None
    price_per_day: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    is_listed: Optional[bool] = None

    class Config:
        from_attributes = True


class CarDisplay(BaseModel):
    id: int
    owner: UserDisplay
    make: str
    model: str
    year: int
    transmission_type: str
    motor_type: str
    price_per_day: float
    description: Optional[str]
    is_listed: bool

    class Config:
        from_attributes = True
