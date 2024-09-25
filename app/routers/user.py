from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.schemas.car import CarDisplay
from app.schemas.user import UserProfile
from app.services import car, user

router = APIRouter(prefix="/user", tags=["user"])


@router.put("/profile")
def modify_user_profile(
        user_profile: UserProfile,
        db: Session = Depends(database.get_db),
        current_user=Depends(oauth2.get_current_user)
):
    return user.modify_user_profile(user_profile, db)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    return user.delete_user(user_id, db)

@router.get("/cars/{user_id}", response_model=List[CarDisplay])
def read_cars_by_user(user_id: int, db: Session = Depends(database.get_db)):
    cars = car.get_cars_by_user(db, user_id)
    if not cars:
        raise HTTPException(status_code=404, detail="Cars not found for this user")
    return cars
