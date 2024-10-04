from typing import Dict, List, Optional, Union

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.schemas.car import CarDisplay
from app.schemas.enums import UserType
from app.schemas.user import (
    UserBase,
    UserDisplay,
    UserProfileForm,
    UserPublicDisplay,
    create_user_private_display,
    create_user_public_display,
)
from app.services import car as car_service
from app.services import user as user_service
from app.utils import constants

router = APIRouter(prefix="/users", tags=["users"])


def check_user_id_and_path_parameter(user_id: int, path_param: int):
    if user_id != path_param:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Can not query another users.",
        )


@router.get(
    "",
    response_model=Dict[str, Union[Optional[int], List[UserDisplay]]],
    summary="Get all users (admin only) (paginated)",
)
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


@router.get("/{user_id}", response_model=Union[UserDisplay, UserPublicDisplay])
def get_user(
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    if current_user.id == user_id:
        return create_user_private_display(user_service.get_user_by_id(user_id, db))
    return create_user_public_display(user_service.get_user_by_id(user_id, db))


@router.put("/{user_id}", response_model=Dict[str, Union[UserDisplay, bool]])
def modify_user_profile(
    user_profile: UserProfileForm,
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    check_user_id_and_path_parameter(current_user.id, user_id)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user profile data is missing.",
        )
    return user_service.modify_user(current_user.id, user_profile, db)


@router.post("/{user_id}/profile-picture")
def upload_profile_picture(
    picture: UploadFile = File(
        ...,
        description="Upload an image (JPEG, PNG, BMP, WEBP)",
        openapi_extra={"examples": {"image": {"content": {"image/*": {}}}}},
    ),
    current_user=Depends(oauth2.get_current_user),
):
    if not picture:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Provide a picture"
        )
    return user_service.upload_user_profile_picture(picture, current_user.id)


@router.delete("")
def delete_user(
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return user_service.delete_user(current_user.id, db)


@router.get("/{user_id}/cars", response_model=List[CarDisplay], tags=["user", "cars"])
def read_cars_by_user(
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    check_user_id_and_path_parameter(current_user.id, user_id)
    cars = car_service.get_cars_by_user(db, user_id)
    if not cars:
        raise HTTPException(status_code=404, detail="Cars not found for this user")
    return cars


@router.put(
    "/{user_id}/password",
    summary="Change password",
    description="This endpoint is used to change user's password.",
)
def change_password(
    new_password: str,
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    check_user_id_and_path_parameter(current_user.id, user_id)
    return user_service.change_password(user_id, new_password, db)
