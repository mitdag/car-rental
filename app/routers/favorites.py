from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.schemas.favorites import FavoritesBase
from app.schemas.user import UserBase
from app.services import favorites as favorites_service

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("", response_model=List[FavoritesBase])
def get_favorites_for_user(
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    return favorites_service.get_favorites_for_user(current_user, db)


@router.post("/{car_id}", response_model=FavoritesBase)
def add_to_favorites(
    car_id: int,
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    return favorites_service.add_to_favorite(car_id, current_user, db)


@router.delete("/{car_id}")
def remove_from_favorites(
    car_id: int,
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    return favorites_service.remove_from_favorites(car_id, current_user, db)
