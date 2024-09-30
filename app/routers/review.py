from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import oauth2  # Assuming a valid OAuth2 authentication set up
from app.core.database import get_db
from app.schemas.review import ReviewBase, ReviewDisplay
from app.services import review  

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewDisplay)
def create_review(
    request: ReviewBase, 
    db: Session = Depends(get_db), 
    current_user=Depends(oauth2.get_current_user)  # Uncomment this line to enable authentication
):
    """Create a new review."""
    return review.create_review(db, request)


@router.get("/", response_model=List[ReviewDisplay])
def read_reviews(db: Session = Depends(get_db)):
    """Retrieve all reviews."""
    return review.get_all_reviews(db)


@router.get("/{review_id}", response_model=ReviewDisplay)
def read_review(review_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific review by ID."""
    db_review = review.get_review_by_id(db, review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review


@router.put("/{review_id}", response_model=ReviewDisplay)
def update_review(
    review_id: int, 
    request: ReviewBase, 
    db: Session = Depends(get_db), 
    current_user=Depends(oauth2.get_current_user)  # Uncomment this line to enable authentication
):
    """Update a specific review by ID."""
    db_review = review.get_review(db, review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review.update_review(db, review_id, request)


@router.delete("/{review_id}")
def delete_review(
    review_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(oauth2.get_current_user)  # Uncomment this line to enable authentication
):
    """Delete a specific review by ID."""
    db_review = review.delete_review(db, review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"detail": "Review deleted successfully"}