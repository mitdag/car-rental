from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import Query, HTTPException
from pydantic import BaseModel, Field, model_validator
from starlette import status

import app.utils.constants as constants


class RentalBase(BaseModel):
    car_id: int
    start_date: datetime
    end_date: datetime
    status: str
    class Config:
        extra = "forbid"  # Prevents extra fields


class RentalDisplay(RentalBase):
    id: int
    renter_id: int
    total_price: float

    class Config:
        orm_mode = True


class RentalPeriod(BaseModel):
    start_date: Optional[datetime] = Field(
        Query(default=None, description="Rental period from this day")
    )
    end_date: Optional[datetime] = Field(
        Query(default=None, description="Rental period until this day")
    )

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def validate_dates(cls, values):
        start: datetime = values["start_date"]
        end: datetime = values["end_date"]
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
        if start > datetime.now() + timedelta(
            weeks=constants.LATEST_START_DATE_OF_RENTAL_IN_WEEKS
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rental start date must be within {constants.LATEST_START_DATE_OF_RENTAL_IN_WEEKS} weeks",
            )
        if int((end - start).days / 7) > constants.MAX_RENTAL_PERIOD_IN_WEEKS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Max rental period is {constants.MAX_RENTAL_PERIOD_IN_WEEKS} weeks",
            )

        return values
