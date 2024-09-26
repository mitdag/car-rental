from sqlalchemy.orm import Session
from app import models, schemas
from app.models.review import DBReview
from app.schemas.review import ReviewBase, ReviewDisplay

# Create a new review
def create_review(db: Session, review: ReviewBase):
    db_review = models.Review(
        rental_id=review.rental_id,
        reviewer_id=review.reviewer_id,
        reviewee_id=review.reviewee_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

# Get a review by ID
def get_review(db: Session, review_id: int):
    return db.query(DBReview).filter(DBReview.review_id == review_id).first()

# Get all reviews
def get_reviews(db: Session, skip: int = 0, limit: int = 10):
    return db.query(DBReview).offset(skip).limit(limit).all()

# Update a review
def update_review(db: Session, review_id: int, review: ReviewDisplay):
    db_review = db.query(DBReview).filter(DBReview.review_id == review_id).first()
    if db_review:
        db_review.rating = review.rating
        db_review.comment = review.comment
        db.commit()
        db.refresh(db_review)
    return db_review

# Delete a review
def delete_review(db: Session, review_id: int):
    db_review = db.query(DBReview).filter(DBReview.review_id == review_id).first()
    if db_review:
        db.delete(db_review)
        db.commit()
    return db_review