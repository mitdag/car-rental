from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.rental import RentalBase, RentalDisplay
from app.services.rental import create_rental, get_rental_by_id, get_all_rentals, update_rental, delete_rental
from app.core.database import get_db

#router = APIRouter()
router = APIRouter(prefix="/rentals", tags=["rentals"])

# Create a new rental
@router.post("/", response_model=RentalDisplay)
def create_new_rental(rental: RentalBase, renter_id: int, db: Session = Depends(get_db)):
    return create_rental(db, rental, renter_id)

# Get a rental by ID
@router.get("/{rental_id}", response_model=RentalDisplay)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = get_rental_by_id(db, rental_id)
    if rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental

# Get all rentals
@router.get("/", response_model=list[RentalDisplay])
def get_rentals(db: Session = Depends(get_db)):
    return get_all_rentals(db)

# Update a rental by ID
@router.put("/{rental_id}", response_model=RentalDisplay)
def update_existing_rental(rental_id: int, rental: RentalBase, db: Session = Depends(get_db)):
    updated_rental = update_rental(db, rental_id, rental)
    if updated_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return updated_rental

# Delete a rental by ID
@router.delete("/{rental_id}", response_model=RentalDisplay)
def remove_rental(rental_id: int, db: Session = Depends(get_db)):
    deleted_rental = delete_rental(db, rental_id)
    if deleted_rental is None:
        raise HTTPException(status_code=404, detail="Rental not found")
    return deleted_rental