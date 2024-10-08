from typing import List
from app.services import rental
from fastapi import Query
from app.auth import oauth2
from app.services.rental import create_rental
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.rental import RentalBase, RentalDisplay, RentalPeriod
from app.utils import constants
from app.services.rental import (
    get_rental_by_id,
    update_rental,
    delete_rental,
)
from app.core.database import get_db

# router = APIRouter()
router = APIRouter(prefix="/rentals", tags=["rentals"])


# Create a new rental
@router.post("/", response_model=RentalDisplay)
def create_new_rental(
    car_id: int,
    status: str,
    rental: RentalPeriod = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    print(rental.dict())  # Check what fields are actually being received

    return create_rental(db, car_id, status, rental, current_user.id)


# Get a rental by ID
@router.get("/{rental_id}", response_model=RentalDisplay)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = get_rental_by_id(db, rental_id)
    if rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental


# Get all rentals
# @router.get("/", response_model=List[RentalDisplay])
# def get_rentals(db: Session = Depends(get_db)):
#     # return get_all_rentals(db)
#     return get_rentals(db)


@router.get(
    "/",
    response_model=List[RentalDisplay],
    summary="List all Rentals",
    description="Retrieve a paginated list of all cars from the database.",
)
def list_rentals(
    db: Session = Depends(get_db),
    skip: int = Query(
        0, ge=0, description="Number of records to skip (used for pagination)"
    ),
    limit: int = Query(
        constants.QUERY_LIMIT_DEFAULT,
        ge=1,
        le=constants.QUERY_LIMIT_MAX,
        description="Maximum number of records to return",
    ),
) -> List[RentalDisplay]:
    """
    Retrieve all rental entries from the database with pagination options.

    Args:
        db (Session): Database session dependency.
        skip (int): Number of records to skip (used for pagination).
        limit (int): Maximum number of records to return (used for pagination).

    Returns:
        List[RentalBase]: A list of rentals in the database based on pagination.
    """
    return rental.get_all_rentals(db, skip=skip, limit=limit)


# Update a rental by ID
@router.put("/{rental_id}", response_model=RentalDisplay)
def update_existing_rental(
    rental_id: int,
    rental: RentalBase,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    updated_rental = update_rental(db, rental_id, rental)
    if updated_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return updated_rental


# Delete a rental by ID
@router.delete("/{rental_id}", response_model=RentalDisplay)
def remove_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    deleted_rental = delete_rental(db, rental_id)
    if deleted_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return deleted_rental
