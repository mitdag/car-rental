from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, conint

# Here under is what is added
from app.schemas.user import UserPublicDisplay


# Review Schema
class ReviewBase(BaseModel):
    rental_id: int
    reviewer_id: int
    reviewee_id: int
    rating: conint(ge=1, le=5)  # Rating must be between 1 and 5
    comment: Optional[str] = None

    # comment: constr(max_length=500)  # Comment must be max 500 characters


# class ReviewCreate(BaseModel):
#     rental_id: int
#     reviewer_id: int
#     reviewee_id: int
#     rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")
#     comment: str = Field(..., max_length=500)

#     # ratting: conint(ge=1, le=5)
#     # comment: constr(max_length=500)


class ReviewCreate(BaseModel):
    rental_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")
    comment: str = Field(..., max_length=500)
    # reviewee_id: Optional[int]

    # ratting: conint(ge=1, le=5)
    # comment: constr(max_length=500)


# class ReviewDisplay(ReviewCreate):
class ReviewDisplay(BaseModel):
    id: Optional[int]
    rental_id: Optional[int]
    reviewer_id: Optional[int]
    reviewee_id: Optional[int]
    rating: Optional[int]
    comment: Optional[str] = None
    reviewer: Optional[UserPublicDisplay]
    reviewee: Optional[UserPublicDisplay]
    review_date: Optional[datetime]

    class Config:
        from_attributes = True
