import os
import shutil
from pathlib import Path as pathlibPath

from fastapi import UploadFile, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import DBUser
from app.schemas.user import UserProfileForm
from app.services import address as address_service
from app.utils import constants
from app.utils.constants import PROFILE_PICTURES_PATH, DEFAULT_PROFILE_PICTURE_FILE
from app.utils.logger import logger
from app.utils.hash import Hash


def get_user_by_id(user_id: int, db: Session):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )
    return user


def get_user_by_email(email: str, db):
    return (
        db.query(DBUser).filter(func.lower(DBUser.email) == func.lower(email)).first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 20):
    limit = min(limit, constants.QUERY_LIMIT_MAX)
    if skip < 0 or limit < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip and limit must be positive integers",
        )
    total = db.query(func.count(DBUser.id)).scalar()
    users = db.query(DBUser).offset(skip).limit(limit).all()
    return {
        "current_offset": skip,
        "counts": len(users),
        "total_counts": total,
        "next_offset": (skip + limit) if len(users) == limit else None,
        "cars": users,
    }


def get_user_profile(user_id: int, db: Session):
    return db.query(DBUser).join(DBUser.address).filter(DBUser.id == user_id).first()


def modify_user(user_id: int, user_profile: UserProfileForm, db: Session):
    db_user = db.query(DBUser).filter(user_id == DBUser.id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist."
        )

    db_user.is_profile_completed = (
        db_user.last_name != ""
        and db_user.last_name != ""
        and db_user.phone_number != ""
    )

    update_data = user_profile.model_dump(exclude_unset=True, exclude={"address"})
    for key, value in update_data.items():
        setattr(db_user, key, value)

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as exc:
        logger.error(exc)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the car: {str(exc)}",
        )

    # Check if address needs to be updated
    if user_profile.address:
        address_service.update_user_address(
            user=db_user,
            address_update=user_profile.address,
            db=db,
        )
    return db_user


def get_picture_name_and_path(user_id: int):
    current_dir = pathlibPath(os.path.dirname(__file__)).as_posix()
    pictures_path = (
        current_dir[: current_dir.rindex("/")] + "/static/images/profile-pictures"
    )
    file_name_no_ext = f"user_{(str(user_id)):0>6}"
    files = list(
        filter(
            lambda x: x.find(file_name_no_ext) != -1,
            [f for f in os.listdir(pictures_path)],
        )
    )
    return files, file_name_no_ext, pictures_path


def upload_user_profile_picture(picture: UploadFile, user_id: int):
    current_files, file_name_no_ext, pictures_path = get_picture_name_and_path(user_id)
    _, upload_file_ext = os.path.splitext(picture.filename)
    allowed_types = ["image/jpeg", "image/png", "image/bmp", "image/webp"]
    if picture.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. "
            f"Only {', '.join(list(map(lambda t: t.replace('image/', '').upper(), allowed_types)))} types are allowed.",
        )
    for f in current_files:
        os.remove(f"{pictures_path}/{f}")
    with open(f"{pictures_path}/{file_name_no_ext}.{upload_file_ext}", "w+b") as buffer:
        shutil.copyfileobj(picture.file, buffer)
    return {
        "file-name": f"{file_name_no_ext}.{upload_file_ext}",
        "file-type": picture.content_type,
    }


def get_profile_picture_link(user_id: int, db):
    # Check if user exist (get_user_by_id raises exception if the user does not exist)
    get_user_by_id(user_id, db)
    current_files, _, _ = get_picture_name_and_path(user_id)
    profile_picture_file = (
        DEFAULT_PROFILE_PICTURE_FILE if len(current_files) == 0 else current_files[0]
    )
    return f"static/{PROFILE_PICTURES_PATH}/{profile_picture_file}"


def delete_profile_picture(user_id: int, db):
    current_files, file_name_no_ext, pictures_path = get_picture_name_and_path(user_id)
    if len(current_files) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User has no profile picture"
        )
    for f in current_files:
        os.remove(f"{pictures_path}/{f}")
    return "deleted"


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
    return {"user_id": user.id, "result": "Password is changed"}


def get_user_rentals(user_id: int, db: Session):
    user: DBUser = db.query(DBUser).filter(DBUser.id == user_id).all()
    return user.rentals
