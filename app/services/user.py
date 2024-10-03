import os
import shutil

from fastapi import status, UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from pathlib import Path as pathlib_path

from app.models.user import DBUser
from app.schemas.address import AddressForm
from app.schemas.user import UserProfileForm
from app.services import address as address_service
from app.utils.hash import Hash


def get_user_by_id(user_id: int, db: Session):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
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


def modify_user(user_id: int, user_profile: UserProfileForm, db: Session):
    user = db.query(DBUser).filter(user_id == DBUser.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist."
        )

    changed = False
    if user_profile.name:
        user.name = user_profile.name
        changed = True
    if user_profile.last_name:
        user.last_name = user_profile.last_name
        changed = True
    if user_profile.phone_number:
        user.phone_number = user_profile.phone_number
        changed = True
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No update is received"
        )
    user.is_profile_completed = (
        user.last_name != "" and user.last_name != "" and user.phone_number != ""
    )

    db.add(user)
    db.commit()
    db.flush(user)

    address_profile = address_service.update_user_address(
        user=user,
        address_profile=AddressForm(
            street=user_profile.street,
            number=user_profile.number,
            postal_code=user_profile.postal_code,
            city=user_profile.city,
            state=user_profile.state,
            country=user_profile.country,
            is_address_confirmed=False,
        ),
        db=db,
    )
    return {
        "profile": user,
        "is_profile_completed": user.is_profile_completed,
        "is_address_confirmed": (
            address_profile and address_profile.latitude and address_profile.longitude
        )
        is not None,
    }


def upload_user_profile_picture(picture: UploadFile, user_id: int):
    current_dir = pathlib_path(os.path.dirname(__file__)).as_posix()
    pictures_path = (
        current_dir[: current_dir.rindex("/")] + "/static/images/profile-pictures"
    )

    _, upload_file_ext = os.path.splitext(picture.filename)
    file_name = f"user_{(str(user_id)):0>6}{upload_file_ext}"
    allowed_types = ["image/jpeg", "image/png", "image/bmp", "image/webp"]
    if picture.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. "
            f"Only {', '.join(list(map(lambda t: t.replace('image/', '').upper(), allowed_types)))} types are allowed.",
        )

    with open(f"{pictures_path}/{file_name}", "w+b") as buffer:
        shutil.copyfileobj(picture.file, buffer)
    return {"file-name": file_name, "file-type": picture.content_type}


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


def change_password(user_id: int, new_password: str, db: Session):
    if not new_password or new_password.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty password"
        )

    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such user"
        )

    user.password = Hash.bcrypt(new_password.strip())
    db.commit()
    db.flush(user)
    return {"user_id": user, "result": "Password is changed"}
