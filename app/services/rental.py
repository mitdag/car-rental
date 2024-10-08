from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.rental import DBRental
from app.models.user import DBUser
from app.schemas.enums import RentalStatus, RentalSort, SortDirection
from app.services.car import get_car
from typing import List, Dict, Union

from app.schemas.rental import RentalBase, RentalPeriod
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import aliased
from datetime import datetime
import app.utils.constants as constants


# Create a new rental


def create_rental(db: Session, car_id, rental: RentalPeriod, renter_id: int):
    car = get_car(db, car_id)
    if car.owner_id == renter_id:
        raise HTTPException(status_code=404, detail="You are the owner of the car!")
    if not is_car_available(car_id, rental.start_date, rental.end_date, db):
        raise HTTPException(
            status_code=404, detail="Car is not available during this period!"
        )
    db_rental = DBRental(
        car_id=car_id,
        renter_id=renter_id,
        start_date=rental.start_date,
        end_date=rental.end_date,
        total_price=(rental.end_date - rental.start_date).days * car.price_per_day,
        status=RentalStatus.RESERVED,
    )
    db.add(db_rental)
    db.commit()
    db.refresh(db_rental)
    return db_rental


# Retrieve rental by ID
def get_rental_by_id(db: Session, rental_id: int):
    return db.query(DBRental).filter(DBRental.id == rental_id).first()


# Retrieve all rentals
# def get_all_rentals(db: Session):
#     return db.query(DBRental).all()


def get_all_rentals(
    db,
    current_user: DBUser,
    rental_id: int = None,
    sort_by: RentalSort = RentalSort.DATE,
    sort_dir: SortDirection = SortDirection.ASC,
    car_id: int = None,
    skip: int = 0,
    limit: int = constants.QUERY_LIMIT_DEFAULT,
) -> Dict[str, Union[int, List[DBRental]]]:
    limit = min(limit, constants.QUERY_LIMIT_MAX)

    q_filer = [
        current_user.id == DBRental.renter_id,
        DBRental.renter_id == rental_id if rental_id else True,
        DBRental.car_id == car_id if car_id else True,
    ]
    if sort_by == RentalSort.DATE:
        q_sort = DBRental.start_date
    elif sort_by == RentalSort.TOTAL_PRICE:
        q_sort = DBRental.total_price
    else:
        q_sort = DBRental.status

    if sort_dir == SortDirection.ASC:
        q_sort = q_sort.asc()
    else:
        q_sort = q_sort.desc()

    total = db.query(func.count(DBRental.id)).filter(and_(*q_filer)).scalar()

    rentals = (
        db.query(DBRental)
        .filter(and_(*q_filer))
        .order_by(q_sort)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {
        "current_offset": skip,
        "counts": len(rentals),
        "total_counts": total,
        "next_offset": (skip + limit) if len(rentals) == limit else None,
        "rentals": rentals,
    }


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


# new code
def is_car_available(car_id: int, start_date: datetime, end_date: datetime, db):
    rental_t1 = aliased(DBRental)
    rental_t2 = aliased(DBRental)
    result = db.execute(
        select(rental_t1.car_id, rental_t1.start_date, rental_t1.end_date).where(
            and_(
                rental_t1.car_id == car_id,
                rental_t1.car_id.in_(
                    select(rental_t2.car_id).where(
                        and_(
                            rental_t2.car_id == rental_t1.car_id,
                            or_(
                                and_(
                                    start_date >= rental_t2.start_date,
                                    start_date <= rental_t2.end_date,
                                ),
                                and_(
                                    end_date >= rental_t2.start_date,
                                    end_date <= rental_t2.end_date,
                                ),
                            ),
                        )
                    )
                ),
            )
        )
    ).all()
    return len(result) != 0
