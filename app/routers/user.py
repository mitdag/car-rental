import os
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi import Path as FastAPI_Path
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.schemas.car import CarDisplay
from app.schemas.user import UserDisplay, UserProfile
from app.services import car as car_service
from app.services import user as user_service

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/{user_id}", response_model=UserDisplay)
def get_user(user_id: int = FastAPI_Path(...), db: Session = Depends(database.get_db)):
    return user_service.get_user_by_id(user_id, db)


@router.put("/{user_id}/profile")
def modify_user_profile(
    user_profile: UserProfile,
    user_id: int = FastAPI_Path(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    if oauth2.can_call_this_api(current_user, user_id):
        return user_service.modify_user_profile(user_id, user_profile, db)


@router.post("/{user_id}/profile-picture")
def upload_profile_picture(
    user_id: int = FastAPI_Path(...),
    picture: UploadFile = File(...),
    current_user=Depends(oauth2.get_current_user),
):
    if oauth2.can_call_this_api(current_user, user_id):
        current_dir = Path(os.path.dirname(__file__)).as_posix()
        pictures_path = (
            current_dir[: current_dir.rindex("/")] + "/static/images/profile-pictures"
        )
        # TODO frontend must control the picture file has an extension
        _, upload_file_ext = os.path.splitext(picture.filename)
        file_name = f"user_{(str(user_id)):0>6}{upload_file_ext}"

        with open(f"{pictures_path}/{file_name}", "w+b") as buffer:
            shutil.copyfileobj(picture.file, buffer)
        return {"file-name": file_name, "file-type": picture.content_type}


@router.delete("/{user_id}")
def delete_user(
    user_id: int = FastAPI_Path(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    if oauth2.can_call_this_api(current_user, user_id):
        return user_service.delete_user(user_id, db)


@router.get("/{user_id}/cars", response_model=List[CarDisplay], tags=["user", "car"])
def read_cars_by_user(
    user_id: int = FastAPI_Path(...), db: Session = Depends(database.get_db)
):
    cars = car_service.get_cars_by_user(db, user_id)
    if not cars:
        raise HTTPException(status_code=404, detail="Cars not found for this user")
    return cars
