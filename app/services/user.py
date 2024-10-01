from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.models.user import DBUser
from app.schemas.address import AddressDisplay
from app.schemas.user import UserProfileForm
from app.services import address as address_service


def get_user_by_id(user_id: int, db: Session):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    # user = db.query(DBUser).options(joinedload(DBUser.cars)).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )
    return user


def get_user_by_email(email: str, db: Session):
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )
    return user


def get_users(db: Session, skip: int, limit: int = 20):
    if skip < 0 or limit < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip and limit must be positive integers",
        )
    result = db.query(DBUser).offset(skip).limit(limit).all()
    return {
        "next_offset": (skip + limit) if len(result) == limit else None,
        "users": result,
    }


def get_user_profile(user_id: int, db: Session):
    return db.query(DBUser).join(DBUser.address).filter(DBUser.id == user_id).first()


def modify_user_profile(user_id: int, user_profile: UserProfileForm, db: Session):
    user = db.query(DBUser).filter(user_id == DBUser.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist."
        )

    user.name = "" if not user_profile.name else user_profile.name.strip()
    user.last_name = (
        "" if not user_profile.last_name else user_profile.last_name.strip()
    )
    user.phone_number = (
        "" if not user_profile.phone_number else user_profile.phone_number.strip()
    )
    user.is_profile_completed = (
        user.last_name != "" and user.last_name != "" and user.phone_number != ""
    )

    db.add(user)
    db.commit()
    db.flush(user)

    address_profile = address_service.update_user_address(
        user_id=user_id,
        address_profile=AddressDisplay(
            street=user_profile.street,
            number=user_profile.number,
            postal_code=user_profile.postal_code,
            city=user_profile.city,
            state=user_profile.state,
            country=user_profile.country,
        ),
        db=db,
    )
    return {
        "profile": user_profile,
        "is_profile_completed": user.is_profile_completed,
        "is_address_confirmed": (address_profile.latitude and address_profile.longitude)
        is not None,
    }


def delete_user(user_id: int, db: Session):
    user = db.query(DBUser).filter(user_id == DBUser.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist."
        )

    db.delete(user)
    db.commit()
    return "Deleted"


def is_user_profile_complete(user_id, db):
    user = db.query(DBUser).filter(user_id == DBUser.id).first()
    if not user:
        return False
    else:
        return (
            user.phone_number != ""
            and user.is_verified
            and address_service.is_user_address_complete(user_id, db)
        )
