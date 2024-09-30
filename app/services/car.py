from typing import List, Optional
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, literal_column, and_, func

from app.models.address import DBAddress
from app.models.car import DBCar
from app.models.user import DBUser
from app.schemas.car import CarBase
from app.schemas.enums import CarSearchSortType, CarSearchSortDirection
from app.services.user import get_user_by_id
from app.utils.logger import logger


# Database Operations


def create_car(db: Session, car: CarBase) -> DBCar:
    db_car = DBCar(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


def get_car(db: Session, car_id: int) -> Optional[DBCar]:
    car = db.query(DBCar).filter(DBCar.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


def get_cars(db: Session, skip: int = 0, limit: int = 100) -> List[DBCar]:
    return db.query(DBCar).offset(skip).limit(limit).all()


def update_car(db: Session, car_id: int, car_update: CarBase) -> Optional[DBCar]:
    if car_update.owner_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="owner_id must be provided."
        )
    try:
        get_car(db, car_id)
    except Exception as exc:
        logger.error(exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {car_id} does not exist.",
        )
    try:
        get_user_by_id(car_update.owner_id, db)
    except Exception as exc:
        logger.error(exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {car_update.owner_id} does not exist.",
        )

    db_car = get_car(db, car_id)
    if db_car:
        update_data = car_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_car, key, value)
        db.commit()
        db.refresh(db_car)
    return db_car


def delete_car(db: Session, car_id: int) -> Optional[DBCar]:
    db_car = get_car(db, car_id)
    if db_car:
        db.delete(db_car)
        db.commit()
    return db_car


def get_cars_by_user(db: Session, user_id: int) -> List[DBCar]:
    cars = db.query(DBCar).filter(DBCar.owner_id == user_id).all()
    if not cars:
        raise HTTPException(status_code=404, detail="No cars found for this user.")
    return cars


def search_cars(
    distance_km: float,
    renter_lat: float,
    renter_lon: float,
    booking_date_start: datetime,
    booking_date_end: datetime,
    search_in_city: str,
    engine_type: str,
    transmission_type: str,
    price_min: int,
    price_max: int,
    make: str,
    sort: CarSearchSortType,
    sort_direction: CarSearchSortDirection,
    skip: int,
    limit: int,
    db: Session,
):
    if (
        not distance_km
        and not booking_date_start
        and not search_in_city
        and not engine_type
        and not transmission_type
        and not price_min
        and not price_max
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specify at least one search parameter",
        )
    if distance_km and not search_in_city and (not renter_lat or not renter_lon):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Distance without location info. Specify a location to search (city or lat and lon)",
        )
    # if city and distance both exists ignore lat and lon
    if distance_km and search_in_city:
        distance_km = None
    if not booking_date_end:
        booking_date_end = datetime.utcnow()

    sort_by = None
    if sort:
        if not sort_direction:
            sort_direction = CarSearchSortDirection.ASC
        if sort == CarSearchSortType.DISTANCE:
            sort_by = (
                literal_column("distance").asc()
                if sort_direction == CarSearchSortDirection.ASC
                else literal_column("distance").desc()
            )
        elif sort == CarSearchSortType.ENGINE_TYPE:
            sort_by = (
                DBCar.motor_type.asc()
                if sort_direction == CarSearchSortDirection.ASC
                else DBCar.motor_type.desc()
            )
        elif sort == CarSearchSortType.TRANSMISSION_TYPE:
            sort_by = (
                DBCar.transmission_type.asc()
                if sort_direction == CarSearchSortDirection.ASC
                else DBCar.transmission_type.desc()
            )
        elif sort == CarSearchSortType.MAKE:
            sort_by = (
                DBCar.make.asc()
                if sort_direction == CarSearchSortDirection.ASC
                else DBCar.make.desc()
            )
        elif sort == CarSearchSortType.PRICE:
            sort_by = (
                DBCar.price_per_day.asc()
                if sort_direction == CarSearchSortDirection.ASC
                else DBCar.price_per_day.desc()
            )

    queries = [
        DBUser.id.label("owner_id"),
        DBUser.name.label("owner_name"),
        DBUser.last_name.label("owner_last_name"),
        DBAddress.city,
        DBAddress.latitude,
        DBAddress.longitude,
        DBCar.id.label("car_id"),
        DBCar.motor_type,
        DBCar.price_per_day,
        DBCar.transmission_type,
        DBCar.make,
        DBCar.model,
        DBCar.year,
        DBCar.description,
    ]
    where_clause = [DBUser.id == DBAddress.user_id, DBUser.id == DBCar.owner_id]
    if renter_lat and renter_lon:
        queries.append(
            (
                6371.0
                * func.acos(
                    func.cos(func.radians(renter_lat))
                    * func.cos(func.radians(DBAddress.latitude))
                    * func.cos(
                        func.radians(DBAddress.longitude) - func.radians(renter_lon)
                    )
                    + func.sin(func.radians(renter_lat))
                    * func.sin(func.radians(DBAddress.latitude))
                )
            ).label("distance")
        )
        where_clause.append(DBUser.id == DBAddress.user_id)
    if distance_km:
        where_clause.append(literal_column("distance") < distance_km)
    if search_in_city:
        where_clause.append(DBUser.id == DBAddress.user_id)
        where_clause.append(DBAddress.city == search_in_city)
    if engine_type:
        where_clause.append(DBCar.motor_type == engine_type)
    if transmission_type:
        where_clause.append(DBCar.transmission_type == transmission_type)
    if price_min:
        where_clause.append(DBCar.price_per_day >= price_min)
    if price_max:
        where_clause.append(DBCar.price_per_day <= price_max)
    if make:
        where_clause.append(DBCar.make == make)
    if booking_date_start:
        # TODO implement after rental
        pass
    result = (
        db.execute(
            select(*queries)
            .where(and_(*where_clause))
            .order_by(sort_by)
            .offset(skip)
            .limit(limit)
        )
        .mappings()
        .all()
    )

    return {
        "cars": result,
        "next_offset": (skip + limit) if len(result) == limit else None,
    }
