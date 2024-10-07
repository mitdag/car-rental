from fastapi import HTTPException, status
from app.services.car import get_car
from sqlalchemy.orm import Session

from app.schemas.rental import RentalBase
from app.models.rental import DBRental
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import aliased
from datetime import datetime


# Create a new rental

def create_rental(db: Session, car_id, status, rental: RentalBase, renter_id: int):
    car= get_car(db, car_id)
    if car.owner_id==renter_id:
        raise HTTPException(status_code=404, detail="You are the owner of the car!")
    if not is_car_available(car_id, rental.start_date, rental.end_date, db):
        raise HTTPException(status_code=404, detail="Car is not availbale now!")
    db_rental = DBRental(
        car_id=car_id,
        renter_id=renter_id,
        start_date=rental.start_date,
        end_date=rental.end_date,
        total_price=(rental.start_date - rental.end_date).days*car.price_per_day,
        status=status,
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

#new code
def is_car_available(car_id: int, start_date: datetime, end_date: datetime, db):
    rental_t1 = aliased(DBRental)
    rental_t2 = aliased(DBRental)
    result = db.execute(
            select(rental_t1.car_id).where(
                and_(
                    rental_t1.car_id == car_id,
                    rental_t1.car_id.notin_(
                        select(rental_t2.car_id).where(
                            and_(
                                rental_t2.car_id == rental_t1.car_id,
                                or_(
                                    and_(
                                        start_date >= rental_t2.start_date,
                                        start_date <= rental_t2.end_date
                                    ),
                                    and_(
                                        end_date >= rental_t2.start_date,
                                        end_date <= rental_t2.end_date
                                    )
                                )
                            )
                        )
                    )
                )
            )
    ).all()
    return len(result) != 0