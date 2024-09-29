from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.schemas.user import UserBase
from app.models.favorites import DBFavorite


def get_favorites_for_car(car_id: int, db: Session):
    favorites = db.query(DBFavorite).filter(DBFavorite.car_id == car_id).all()
    return favorites


def get_favorites_for_user(current_user: UserBase, db: Session):
    favorites = db.query(DBFavorite).filter(DBFavorite.user_id == current_user.id).all()
    return favorites


def add_to_favorite(car_id: int, current_user: UserBase, db: Session):
    favorite = DBFavorite()
    favorite.user_id = current_user.id
    favorite.car_id = car_id
    try:
        db.add(favorite)
        db.commit()
        db.flush(favorite)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Primary key already exits."
        )
    return favorite


def remove_from_favorites(car_id, current_user: UserBase, db: Session):
    favorite = (
        db.query(DBFavorite)
        .filter(current_user.id == DBFavorite.user_id and car_id == DBFavorite.car_id)
        .first()
    )
    if favorite:
        db.delete(favorite)
        db.commit()
    return "deleted"
