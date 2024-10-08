from typing import List, Union, Dict, Optional

from app.auth.oauth2 import get_current_user
from app.schemas.enums import RentalSort, SortDirection
from fastapi import Query
from app.auth import oauth2
from app.services.rental import create_rental, get_all_rentals
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.rental import RentalBase, RentalDisplay, RentalPeriod
from app.utils import constants
from app.services.rental import (
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
    rental_period: RentalPeriod = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return create_rental(db, car_id, rental_period, current_user.id)


@router.get(
    "", response_model=Dict[str, Union[Optional[int], Optional[List[RentalDisplay]]]]
)
def get_rentals(
    car_id: int = Query(None),
    rental_id: int = Query(None),
    sort_by: RentalSort = Query(RentalSort.DATE),
    sort_dir: SortDirection = Query(SortDirection.ASC),
    skip: int = Query(0),
    limit: int = Query(constants.QUERY_LIMIT_DEFAULT),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_all_rentals(
        db, current_user, rental_id, sort_by, sort_dir, car_id, skip, limit
    )


# Get a rental by ID
@router.get("/{rental_id}", response_model=Optional[RentalDisplay])
def get_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rentals = get_all_rentals(db=db, rental_id=rental_id, current_user=current_user)
    return (
        rentals["rentals"][0]
        if rentals["rentals"] and len(rentals["rentals"]) > 0
        else None
    )
    # rental_db = get_rental_by_id(db, rental_id)
    # if rental_db is None:
    #     raise HTTPException(status_code=404, detail="Rental not found")
    # return rental_db


# Get all rentals
# @router.get("/", response_model=List[RentalDisplay])
# def get_rentals(db: Session = Depends(get_db)):
#     # return get_all_rentals(db)
#     return get_rentals(db)


# @router.get(
#     "/",
#     response_model=List[RentalDisplay],
#     summary="List all Rentals",
#     description="Retrieve a paginated list of all cars from the database.",
# )
# def list_rentals(
#         db: Session = Depends(get_db),
#         skip: int = Query(
#             0, ge=0, description="Number of records to skip (used for pagination)"
#         ),
#         limit: int = Query(
#             constants.QUERY_LIMIT_DEFAULT,
#             ge=1,
#             le=constants.QUERY_LIMIT_MAX,
#             description="Maximum number of records to return",
#         ),
# ) -> List[RentalDisplay]:
#     """
#     Retrieve all rental entries from the database with pagination options.
#
#     Args:
#         db (Session): Database session dependency.
#         skip (int): Number of records to skip (used for pagination).
#         limit (int): Maximum number of records to return (used for pagination).
#
#     Returns:
#         List[RentalBase]: A list of rentals in the database based on pagination.
#     """
#     return rental.get_all_rentals(db, skip=skip, limit=limit)


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
