from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.car import DBCar
from app.schemas.car import CarBase
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
    car = db.query(DBCar).filter(DBCar.car_id == car_id).first()
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
