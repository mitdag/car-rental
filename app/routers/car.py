from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core.database import get_db
from app.schemas.car import CarBase, CarDisplay
from app.services import car

router = APIRouter(prefix="/car", tags=["car"])


@router.post("/", response_model=CarDisplay)
def create_car(
    request: CarBase,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return car.create_car(db, request)


@router.get("/", response_model=List[CarDisplay])
def read_cars(db: Session = Depends(get_db)):
    return car.get_cars(db)


@router.get("/{car_id}", response_model=CarDisplay)
def read_car(car_id: int, db: Session = Depends(get_db)):
    return car.get_car(db, car_id)


@router.put("/{car_id}")
def update_car(
    car_id: int,
    request: CarBase,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return car.update_car(db, car_id, request)


@router.delete("/{car_id}")
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return car.delete_car(db, car_id)
