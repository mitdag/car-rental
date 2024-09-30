from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Review Schema
class ReviewBase(BaseModel):
    rental_id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: Optional[str] = None


class ReviewDisplay(ReviewBase):
    id: int
    review_date: datetime

    class Config:
        orm_mode = True
