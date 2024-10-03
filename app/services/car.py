from datetime import datetime
from typing import List, Optional, Dict, Union

from fastapi import HTTPException, status
from sqlalchemy import and_, func, literal_column, select
from sqlalchemy.orm import Session

from app.models.address import DBAddress
from app.models.car import DBCar
from app.models.user import DBUser
from app.schemas.car import CarBase, CarUpdate
from app.schemas.enums import (
    CarSearchSortDirection,
    CarSearchSortType,
    CarTransmissionType,
    CarEngineType,
)
from app.utils.logger import logger

# Database Operations


def create_car(db: Session, car: CarBase, user_id: int) -> DBCar:
    db_car = DBCar(**car.model_dump(), owner_id=user_id)
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


def update_car(db: Session, car_id: int, car_update: CarUpdate) -> Optional[DBCar]:
    # For admin endpoint
    # if car_update.owner_id is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, detail="owner_id must be provided."
    #     )
    # try:
    #     get_car(db, car_id)
    # except Exception as exc:
    #     logger.error(exc)
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"Car with ID {car_id} does not exist.",
    #     )
    # For admin endpoint
    # try:
    #     get_user_by_id(car_update.owner_id, db)
    # except Exception as exc:
    #     logger.error(exc)
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"User with ID {car_update.owner_id} does not exist.",
    #     )

    db_car = get_car(db, car_id)
    if db_car:
        update_data = car_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_car, key, value)

        try:
            db.add(db_car)
            db.commit()
            db.refresh(db_car)
        except Exception as exc:
            logger.error(exc)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while updating the car: {str(exc)}",
            )
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
    engine_type: CarEngineType,
    transmission_type: CarTransmissionType,
    price_min: int,
    price_max: int,
    make: str,
    sort: CarSearchSortType,
    sort_direction: CarSearchSortDirection,
    skip: int,
    limit: int,
    db: Session,
) -> Dict[str, Union[Optional[int], List[DBCar]]]:
    """
    :param distance_km: Distance from the renter or the city (if city is specified renter location is ignored)
    :param renter_lat: Latitude of the renter in degrees
    :param renter_lon: Longitude of the renter in degrees
    :param booking_date_start: Start date of the booking
    :param booking_date_end: End date of the booking
    :param search_in_city: Name of the city to search in
    :param engine_type: Type of the car's engine
    :param transmission_type: Type of the car's transmission
    :param price_min: Minimum price per day
    :param price_max: Maximum price per day
    :param make: Make of the car
    :param sort: The column name according to which the result list will be sorted.
    :param sort_direction: Direction of the sort
    :param skip: Offset for pagination
    :param limit: Maximum length of the resulting list
    :param db: App session
    :return: A dictionary of:
        {
            "current_offset": Value of parameter skip (int),
            "counts": Length of the resulting DBCar list (int)
            "total_counts": Total number of matches ignoring the limit value,
            "next_offset": Starting index of the following request in pagination (None if no more records exist),
            "cars": List of matching DBCar objects
        }
    """
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
        # Ignore the sort request if it is "DISTANCE" and a distance value is not provided
        if distance_km and sort == CarSearchSortType.DISTANCE:
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

    selected_attrs = [
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

    # Query for distance calculation. The resulting value will appear as "distance" in query result.
    position_field = None
    if renter_lat and renter_lon:
        position_field = (
            6371.0
            * func.acos(
                func.cos(func.radians(renter_lat))
                * func.cos(func.radians(DBAddress.latitude))
                * func.cos(func.radians(DBAddress.longitude) - func.radians(renter_lon))
                + func.sin(func.radians(renter_lat))
                * func.sin(func.radians(DBAddress.latitude))
            )
        ).label("distance")
        selected_attrs.append(position_field)
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

    # Query for counting the matches without applying the limit value. If search is based on distance,
    # the query for distance calculation must also be included in this query (since "distance" is literal value).
    if distance_km:
        total_counts = (
            db.execute(
                select(
                    position_field, func.count(DBCar.id).label("total_counts")
                ).where(and_(*where_clause))
            )
            .mappings()
            .first()
        )
    else:
        total_counts = (
            db.execute(
                select(func.count().label("total_counts")).where(and_(*where_clause))
            )
            .mappings()
            .first()
        )
    cars = (
        db.execute(
            select(*selected_attrs)
            .where(and_(*where_clause))
            .order_by(sort_by)
            .offset(skip)
            .limit(limit)
        )
        .mappings()
        .all()
    )
    result = {
        "current_offset": skip,
        "counts": len(cars),
        "total_counts": total_counts["total_counts"],
        "next_offset": (skip + limit) if len(cars) == limit else None,
        "cars": cars,
    }
    return result
