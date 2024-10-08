from typing import List, Union, Dict, Optional

from app.auth.oauth2 import get_current_user
from app.schemas.enums import RentalSort, SortDirection
from fastapi import Query, status
from fastapi.responses import JSONResponse
from app.auth import oauth2
from app.services.rental import create_rental, get_all_rentals, get_rental_by_id
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.rental import RentalDisplay, RentalPeriod
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
    if not rental_period.start_date or not rental_period.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide a start and and date",
        )
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
        db, current_user, rental_id, car_id, sort_by, sort_dir, skip, limit
    )


# Get a rental by ID
@router.get("/{rental_id}", response_model=Optional[RentalDisplay])
def get_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    rental_db = get_rental_by_id(db, rental_id, current_user)
    if rental_db is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental_db


# Update a rental by ID
@router.put("/{rental_id}", response_model=RentalDisplay)
def update_existing_rental(
    rental_id: int,
    rental: RentalPeriod = Depends(),
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return update_rental(db, current_user, rental_id, rental)


# Delete a rental by ID
@router.delete("/{rental_id}")
def remove_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    delete_rental(db, rental_id, current_user)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT, content={"message": "Deleted"}
    )
