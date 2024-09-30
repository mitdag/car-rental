import os
import shutil
from pathlib import Path
from typing import List, Dict, Union, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query
from fastapi import Path as FastAPI_Path, status
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.schemas import constants
from app.schemas.car import CarDisplay
from app.schemas.enums import UserType
from app.schemas.user import UserDisplay, UserProfileForm, UserBase
from app.services import car as car_service
from app.services import user as user_service

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/all", response_model=Dict[str, Union[Optional[int], List[UserDisplay]]])
def get_users(
    skip: int = Query(0, description="Offset start number."),
    limit: int = Query(
        default=constants.QUERY_LIMIT_DEFAULT,
        description=f"Length of the response list (max: {constants.QUERY_LIMIT_MAX})",
    ),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin only endpoint"
        )
    return user_service.get_users(db, skip, min(limit, constants.QUERY_LIMIT_MAX))


@router.get("", response_model=UserDisplay)
def get_user(
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    return user_service.get_user_by_id(current_user.id, db)


@router.put("/profile")
def modify_user_profile(
    user_profile: UserProfileForm,
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return user_service.modify_user_profile(current_user.id, user_profile, db)


@router.post("/profile-picture")
def upload_profile_picture(
    picture: UploadFile = File(...),
    current_user=Depends(oauth2.get_current_user),
):
    current_dir = Path(os.path.dirname(__file__)).as_posix()
    pictures_path = (
        current_dir[: current_dir.rindex("/")] + "/static/images/profile-pictures"
    )
    # TODO frontend must control the picture file has an extension
    _, upload_file_ext = os.path.splitext(picture.filename)
    file_name = f"user_{(str(current_user.id)):0>6}{upload_file_ext}"

    with open(f"{pictures_path}/{file_name}", "w+b") as buffer:
        shutil.copyfileobj(picture.file, buffer)
    return {"file-name": file_name, "file-type": picture.content_type}


@router.delete("")
def delete_user(
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return user_service.delete_user(current_user.id, db)


@router.get("/{user_id}/cars", response_model=List[CarDisplay], tags=["user", "car"])
def read_cars_by_user(
    user_id: int = FastAPI_Path(...), db: Session = Depends(database.get_db)
):
    cars = car_service.get_cars_by_user(db, user_id)
    if not cars:
        raise HTTPException(status_code=404, detail="Cars not found for this user")
    return cars
