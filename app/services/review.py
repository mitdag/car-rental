from datetime import datetime

from sqlalchemy.orm import Session

from app.models.review import DBReview
from app.schemas.review import ReviewBase, ReviewCreate


# Create a new review   
def create_review(
    db: Session, review: ReviewCreate, reviewer_id: int, reviewee_id: int
) -> DBReview:
     #aditional validations
    # Validation 1: Ensure reviewee_id is provided
    if reviewee_id is None:
        raise ValueError("Reviewee ID must be provided.")

    # Validation 2: Ensure the reviewer and reviewee are not the same person
    if reviewer_id == reviewee_id:
        raise ValueError("A reviewer cannot review themselves.")

    # Validation 3: Ensure the rating is within a valid range (1-5, for example)
    if not (1 <= review.rating <= 5):
        raise ValueError("Rating must be between 1 and 5.")

    # # Validation 4: Ensure a comment is provided and not empty
    # if not review.comment or review.comment.strip() == "":
    #     raise ValueError("A comment must be provided.")
    #end of adition
    db_review = DBReview(
        rental_id=review.rental_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
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
