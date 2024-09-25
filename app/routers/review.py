from msilib import schema
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api import review
from services import reviews
from app import schemas
from app.database import get_db
from app.core.database import get_db
from app.schemas.review import ReviewDisplay, ReviewBase			   
							
router = APIRouter(prefix="/reviews", tags=["reviews"])
							
@router.post("/", response_model=ReviewDisplay)
def create_review(review: schemas.r, db: Session = Depends(get_db)):
    return reviews.create_review(db, review)

@router.get("/{review_id}", response_model=ReviewDisplay)
def read_review(review_id: int, db: Session = Depends(get_db)):
    db_review = reviews.get_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review
									   
														 
@router.get("/", response_model=List[ReviewDisplay])
def read_reviews(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return reviews.get_review(db, skip=skip, limit=limit)

@router.put("/{review_id}", response_model=ReviewBase)
def update_review(review_id: int, review: schemas.ReviewUpdate, db: Session = Depends(get_db)):
    
    if read_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return reviews.update_review(db, review_id=review_id, review=review)

@router.delete("/{review_id}", response_model=schemas.ReviewResponse)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    db_review = reviews.delete_review(db, review_id=review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return reviews.delete_review(db, review_id=review_id)

						   
														   
									 