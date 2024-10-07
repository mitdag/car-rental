from typing import List
from fastapi import Query
from app.auth import oauth2
from app.services.rental import create_rental
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.rental import RentalBase, RentalDisplay, RentalPeriod
# from app.services.rental import (
#     create_rental,
#     get_rental_by_id,
#     get_all_rentals,
#     update_rental,
#     delete_rental,
# )
from app.core.database import get_db

# router = APIRouter()
router = APIRouter(prefix="/rentals", tags=["rentals"])


# Create a new rental
@router.post("/", response_model=RentalDisplay)
def create_new_rental(
    car_id: int, status:str,
    rental: RentalPeriod=Depends(), db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user),
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
@router.get("/", response_model=List[RentalDisplay])
def get_rentals(db: Session = Depends(get_db)):
    return get_all_rentals(db)


# Update a rental by ID
@router.put("/{rental_id}", response_model=RentalDisplay)
def update_existing_rental(
    rental_id: int, rental: RentalBase, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)
):
    updated_rental = update_rental(db, rental_id, rental)
    if updated_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return updated_rental


# Delete a rental by ID
@router.delete("/{rental_id}", response_model=RentalDisplay)
def remove_rental(rental_id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user),):
    deleted_rental = delete_rental(db, rental_id)
    if deleted_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return deleted_rental
