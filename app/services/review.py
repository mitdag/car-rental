from sqlalchemy.orm import Session
from app.models.review import DBReview
from app.schemas.review import ReviewBase
from datetime import datetime

# Create a new review
def create_review(db: Session, review: ReviewBase):
    db_review = DBReview(
        rental_id=review.rental_id,
        reviewer_id=review.reviewer_id,
        reviewee_id=review.reviewee_id,
        rating=review.rating,
        comment=review.comment,
        review_date=datetime.utcnow(),
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

# Retrieve review by ID
def get_review_by_id(db: Session, review_id: int):
    return db.query(DBReview).filter(DBReview.id == review_id).first()

# Retrieve all reviews
def get_all_reviews(db: Session):
    return db.query(DBReview).all()

# Update a review
def update_review(db: Session, review_id: int, review: ReviewBase):
    db_review = db.query(DBReview).filter(DBReview.id == review_id).first()
    if db_review:
        db_review.rating = review.rating
        db_review.comment = review.comment
        db.commit()
        db.refresh(db_review)
    return db_review

# Delete a review
def delete_review(db: Session, review_id: int):
    db_review = db.query(DBReview).filter(DBReview.id == review_id).first()
    if db_review:
        db.delete(db_review)
        db.commit()
    return db_review