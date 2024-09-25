from datetime import datetime
from pydantic import BaseModel


class ReviewBase(BaseModel):
    review_id: int
    rental_id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: str
    review_date: datetime


class ReviewDisplay(BaseModel):
    review_id: int
    rental_id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: str
    review_date: datetime

    class Config:
        orm_mode = True
