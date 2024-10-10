from datetime import datetime
from typing import Dict, Union, List

from sqlalchemy.orm import Session
from sqlalchemy import or_, func, and_

from app.models.review import DBReview
from app.models.user import DBUser
from app.schemas.enums import ReviewSort, SortDirection
from app.schemas.review import ReviewBase, ReviewCreate
from app.utils import constants


# Create a new review
def create_review(
    db: Session, review: ReviewCreate, reviewer_id: int, reviewee_id: int
) -> DBReview:
    # aditional validations
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
    # end of adition
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


def get_views_by_user(
    db,
    user_id: int,
    current_user: DBUser,
    sort_by: ReviewSort = ReviewSort.REVIEW_DATE,
    sort_dir: SortDirection = SortDirection.ASC,
    skip: int = 0,
    limit: int = constants.QUERY_LIMIT_DEFAULT,
) -> Dict[str, Union[int, List[DBReview]]]:
    limit = min(limit, constants.QUERY_LIMIT_MAX)

    q_filter = [or_(DBReview.reviewer_id == user_id, DBReview.reviewer_id == user_id)]

    if sort_by == ReviewSort.REVIEW_DATE:
        q_sort = DBReview.review_date
    elif sort_by == ReviewSort.REVIEWER_ID:
        q_sort = DBReview.reviewer_id
    elif sort_by == ReviewSort.REVIEWEE_ID:
        q_sort = DBReview.reviewee_id
    elif sort_by == ReviewSort.RENTAL_ID:
        q_sort = DBReview.id
    else:
        q_sort = DBReview.rating

    if sort_dir == SortDirection.ASC:
        q_sort = q_sort.asc()
    else:
        q_sort = q_sort.desc()

    total = db.query(func.count(DBReview.id)).filter(and_(*q_filter)).scalar()

    reviews = (
        db.query(DBReview)
        .filter(and_(*q_filter))
        .order_by(q_sort)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "current_offset": skip,
        "counts": len(reviews),
        "total_counts": total,
        "next_offset": (skip + limit) if len(reviews) == limit else None,
        "reviews": reviews,
    }
