from typing import Optional

from pydantic import BaseModel


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


class CarDisplay(BaseModel):
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
