from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.car import DBCar
from app.schemas.car import CarBase, CarDisplay

# Database Operations


def create_car(db: Session, car: CarBase) -> DBCar:
    db_car = DBCar(**car.model_dump())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


def get_car(db: Session, car_id: int) -> Optional[DBCar]:
    return db.query(DBCar).filter(DBCar.car_id == car_id).first()


def get_cars(db: Session, skip: int = 0, limit: int = 100) -> List[DBCar]:
    return db.query(DBCar).offset(skip).limit(limit).all()


def update_car(db: Session, car_id: int, car_update: CarDisplay) -> Optional[DBCar]:
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


def get_cars_by_user(db: Session, user_id: int):
    return db.query(DBCar).filter(DBCar.owner_id == user_id).all()
