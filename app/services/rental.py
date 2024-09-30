from sqlalchemy.orm import Session

from app.schemas.rental import RentalBase
from app.models.rental import DBRental

# Create a new rental
def create_rental(db: Session, rental: RentalBase, renter_id: int):
    db_rental = DBRental(
        car_id=rental.car_id,
        renter_id=renter_id,
        start_date=rental.start_date,
        end_date=rental.end_date,
        total_price=rental.total_price,
        status=rental.status,
    )
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental

# Retrieve rental by ID
def get_rental_by_id(db: Session, rental_id: int):
    return db.query(DBRental).filter(DBRental.id == rental_id).first()

# Retrieve all rentals
def get_all_rentals(db: Session):
    return db.query(DBRental).all()

# Update a rental
def update_rental(db: Session, rental_id: int, rental: RentalBase):
    db_rental = db.query(DBRental).filter(DBRental.id == rental_id).first()
    if db_rental:
        db_rental.car_id = rental.car_id
        db_rental.start_date = rental.start_date
        db_rental.end_date = rental.end_date
        db_rental.total_price = rental.total_price
        db_rental.status = rental.status
        db.commit()
        db.refresh(db_rental)
    return db_rental

# Delete a rental
def delete_rental(db: Session, rental_id: int):
    db_rental = db.query(DBRental).filter(DBRental.id == rental_id).first()
    if db_rental:
        db.delete(db_rental)
        db.commit()
    return db_rental