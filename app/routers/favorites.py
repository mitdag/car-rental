from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.schemas.favorites import FavoritesBase
from app.schemas.user import UserBase
from app.services import favorites as favorites_service

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get(
    "",
    summary="Get user favorite cars",
    description="Gets id list of the cars favorited by the current user",
)
def get_favorites_for_user(
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    return favorites_service.get_favorites_for_user(current_user, db)


@router.post(
    "/{car_id}",
    response_model=FavoritesBase,
    summary="Add car to favorite",
    description="Adds the car with given id to current user's favorite",
)
def add_to_favorites(
    car_id: int,
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    return favorites_service.add_to_favorite(car_id, current_user, db)


@router.delete(
    "/{car_id}",
    summary="Remove car from favorite",
    description="Removes the car with given id from current user's favorite",
)
def remove_from_favorites(
    car_id: int,
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    return favorites_service.remove_from_favorites(car_id, current_user, db)
