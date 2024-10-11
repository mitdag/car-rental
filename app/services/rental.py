from datetime import datetime, timedelta
from typing import Dict, List, Union

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

import app.utils.constants as constants
from app.models.car import DBCar
from app.models.rental import DBRental
from app.models.user import DBUser
from app.schemas.enums import RentalSort, RentalStatus, SortDirection
from app.schemas.rental import RentalPeriod
from app.services.car import get_car
from app.utils.logger import logger


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
def get_rental_by_id(db: Session, rental_id: int, current_user: DBUser):
    # Build filter conditions
    try:
        q_filter = [DBRental.id == rental_id]

        # Restrict access to either the renter or the owner, unless the user is an admin
        if not current_user.is_admin():
            q_filter.append(
                or_(
                    DBRental.renter_id
                    == current_user.id,  # The current user is the renter
                    DBCar.owner_id
                    == current_user.id,  # The current user is the car owner
                )
            )

        # Query with a join to the DBCar table
        rental = (
            db.query(DBRental)
            .join(DBCar, DBRental.car_id == DBCar.id)
            .options(joinedload(DBRental.car))
            .filter(and_(*q_filter))
            .first()
        )

        # Handle case where rental is not found
        if rental is None:
            logger.warning(f"Rental with id {rental_id} not found.")
            raise HTTPException(status_code=404, detail="Rental not found")

        return rental

    except HTTPException as e:
        # Let HTTP exceptions propagate without catching them as unexpected
        raise e

    except SQLAlchemyError as e:
        # Log SQLAlchemy errors
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except Exception as e:
        # Catch-all for any other unexpected errors
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# Retrieve all rentals
# def get_all_rentals(db: Session):
#     return db.query(DBRental).all()


def get_rentals(
    db,
    current_user: DBUser,
    rental_id: int = None,
    car_id: int = None,
    sort_by: RentalSort = RentalSort.DATE,
    sort_dir: SortDirection = SortDirection.ASC,
    skip: int = 0,
    limit: int = constants.QUERY_LIMIT_DEFAULT,
) -> Dict[str, Union[int, List[DBRental]]]:
    limit = min(limit, constants.QUERY_LIMIT_MAX)

    q_filer = [
        DBRental.id == rental_id if rental_id else True,
        DBRental.car_id == car_id if car_id else True,
    ]
    if not current_user.is_admin():
        q_filer.append(current_user.id == DBRental.renter_id)

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
def update_rental(
    db: Session, current_user: DBUser, rental_id: int, rental_period: RentalPeriod
):
    if not rental_period.start_date and not rental_period.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No dates received."
        )
    q_filter = [DBRental.id == rental_id]
    if not current_user.is_admin():
        q_filter.append(DBRental.renter_id == current_user.id)
    db_rental = db.query(DBRental).filter(and_(*q_filter)).first()
    if not db_rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No such rental for this user.",
        )

    if not is_car_available_for_update(
        db_rental.car_id,
        rental_period.start_date,
        rental_period.end_date,
        db,
        db_rental.renter_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This car is not available for this period.",
        )

    for key, val in rental_period.model_dump(exclude_unset=True).items():
        setattr(db_rental, key, val)

    try:
        db.commit()
        db.refresh(db_rental)
        return db_rental
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process the request.",
        )


# Delete a rental
def delete_rental(db: Session, rental_id: int, current_user: DBUser):
    db_rental = db.query(DBRental).filter(DBRental.id == rental_id).first()
    if not db_rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such rental"
        )

    if not current_user.is_admin() and current_user.id != db_rental.renter_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User can only delete own rentals.",
        )

    if not current_user.is_admin() and db_rental.status != RentalStatus.RESERVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only reservations can be deleted.",
        )

    try:
        db.delete(db_rental)
        db.commit()
        return db_rental
    except Exception as exc:
        logger.log(
            f"Cannot delete rental with rental_id: {rental_id} "
            f"current_user_id: {current_user.id} ({exc})"
        )


# new code
def get_overlapping_rental(car_id: int, start_date: datetime, end_date: datetime, db):
    rental = (
        db.query(DBRental)
        .filter(
            and_(
                car_id == DBRental.car_id,
                or_(
                    and_(
                        start_date >= DBRental.start_date,
                        start_date <= DBRental.end_date,
                    ),
                    and_(
                        end_date >= DBRental.start_date, end_date <= DBRental.end_date
                    ),
                ),
            )
        )
        .first()
    )
    return rental


def is_car_available(car_id: int, start_date: datetime, end_date: datetime, db):
    overlapping_rental = get_overlapping_rental(car_id, start_date, end_date, db)
    return overlapping_rental is None


def is_car_available_for_update(
    car_id: int, start_date: datetime, end_date: datetime, db, renter_id: int
):
    reserved_period: DBRental = get_overlapping_rental(car_id, start_date, end_date, db)
    if not reserved_period:
        return True
    if reserved_period.renter_id != renter_id:
        return False

    converted_date_start = datetime(
        year=reserved_period.start_date.year,
        month=reserved_period.start_date.month,
        day=reserved_period.start_date.day,
    )
    converted_date_end = datetime(
        year=reserved_period.end_date.year,
        month=reserved_period.end_date.month,
        day=reserved_period.end_date.day,
    )
    is_available = False
    if start_date.date() < reserved_period.start_date:
        is_available = is_car_available(
            car_id,
            start_date + timedelta(seconds=1),
            converted_date_start - timedelta(seconds=1),
            db,
        )
        if not is_available:
            return False
    if end_date.date() > reserved_period.end_date:
        is_available = is_car_available(
            car_id,
            converted_date_end + timedelta(seconds=1),
            end_date - timedelta(seconds=1),
            db,
        )
    return is_available
