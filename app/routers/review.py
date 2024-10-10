from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import oauth2  # Assuming a valid OAuth2 authentication set up
from app.core.database import get_db
from app.schemas.review import ReviewBase, ReviewCreate, ReviewDisplay
from app.services import review
from app.services.car import get_car
from app.services.rental import get_rental_by_id

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/",
    response_model=ReviewDisplay,
    summary="Create a review",
    description="Create a new review entry. Requires authenticated user.",
)
def create_review(
    request: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        oauth2.complete_user_profile_only
    ),  # Adjust based on your auth logic
):
    """
    Create a new review entry in the database.

    Args:
        request (ReviewCreate): The details of the review to create.
        db (Session): Database session dependency.
        current_user (Any): The authenticated user creating the review.

    Returns:
        ReviewDisplay: The newly created review.
    """
    # Fetch the rental by id and ensure it exists
    db_rental = get_rental_by_id(db, request.rental_id, current_user)

    if not db_rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    # Fetch car owner and renter information
    renter_id = db_rental.renter_id
    car = get_car(db, db_rental.car_id)

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    owner_id = car.owner_id

    # Check if the current user is either the renter or the owner of the car
    reviewee_id: Optional[int] = None
    if current_user.id == renter_id:
        reviewee_id = owner_id
    elif current_user.id == owner_id:
        reviewee_id = renter_id

    if current_user.id == renter_id or current_user.id == owner_id:
        # Proceed with creating the review
        return review.create_review(db, request, current_user.id, reviewee_id)
    else:
        # If the user is neither the renter nor the owner, raise a 403 error
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to create a review for this rental",
        )


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
    current_user=Depends(
        oauth2.get_current_user
    ),  # Uncomment this line to enable authentication
):
    """Update a specific review by ID."""
    db_review = review.get_review_by_id(db, review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    # Validation1: Check if the reviewer is allowed to update the review
    # if db_review.reviewer_id != current_user.id:
    #    raise HTTPException(status_code=403, detail="Not authorized to update this review")

    return review.update_review(db, review_id, request)


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        oauth2.get_current_user
    ),  # Uncomment this line to enable authentication
):
    """Delete a specific review by ID."""
    db_review = review.delete_review(db, review_id)
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"detail": "Review deleted successfully"}
