from datetime import datetime
from pydantic import BaseModel


class RentalBase(BaseModel):
    car_id: int
    start_date: datetime
    end_date: datetime
    total_price: float
    status: str
    class Config:
        extra = "forbid"  # Prevents extra fields


class RentalDisplay(RentalBase):
    id: int
    renter_id: int

    class Config:
        orm_mode = True
