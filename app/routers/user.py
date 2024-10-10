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
    Body,
)
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.models.user import DBUser
from app.schemas.car import CarDisplay
from app.schemas.enums import RentalSort, SortDirection, ReviewSort
from app.schemas.rental import RentalDisplay
from app.schemas.review import ReviewDisplay
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
from app.services import rental as rental_service
from app.utils import constants
from app.services import review as review_service

router = APIRouter(prefix="/users", tags=["users"])


def check_user_id_and_path_parameter(user_id: int, path_param: int):
    if user_id != path_param:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Can not query another users.",
        )


@router.get(
    "",
    response_model=Dict[
        str,
        Union[
            Optional[int],
            Optional[List[UserDisplay]],
            Optional[UserDisplay],
            Optional[UserPublicDisplay],
        ],
    ],
    summary="Get users",
    description="Admins can get all users without providing a user_id. Other users must provide "
    "a user_id. Response is tailored according to the user: user gets detailed info "
    "about himself/herself. User can get limited info for other users. Admin gets "
    "details for all users.",
)
def get_users(
    user_id: int = Query(None),
    skip: int = Query(0, description="Offset start number."),
    limit: int = Query(
        default=constants.QUERY_LIMIT_DEFAULT,
        description=f"Length of the response list (max: {constants.QUERY_LIMIT_MAX})",
    ),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    if not current_user.is_admin() and not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A user id must be provided.",
        )
    if user_id:
        if current_user.id == user_id:
            return {
                "user": create_user_private_display(
                    user_service.get_user_by_id(user_id, db)
                )
            }
        return {
            "user": create_user_public_display(user_service.get_user_by_id(user_id, db))
        }

    return user_service.get_users(db, skip, min(limit, constants.QUERY_LIMIT_MAX))


@router.put(
    "/{user_id}",
    response_model=UserDisplay,
)
def update_user(
    user_profile: UserProfileForm,
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(oauth2.get_current_user),
):
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user profile data is missing.",
        )
    if user_id != current_user.id and not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User cannot modify another user.",
        )

    return user_service.modify_user(user_id, user_profile, db)


@router.get(
    "/{user_id}",
    response_model=Dict[str, Union[UserDisplay, Optional[UserPublicDisplay]]],
)
def get_user(
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
    current_user: UserBase = Depends(oauth2.get_current_user),
):
    if current_user.id == user_id or current_user.is_admin():
        return {
            "user": create_user_private_display(
                user_service.get_user_by_id(user_id, db)
            )
        }
    return {
        "user": create_user_public_display(user_service.get_user_by_id(user_id, db))
    }


@router.post("/{user_id}/profile-picture", status_code=status.HTTP_201_CREATED)
def upload_profile_picture(
    user_id: int = Path(...),
    picture: UploadFile = File(
        ...,
        description="Upload an image (JPEG, PNG, BMP, WEBP)",
        openapi_extra={"examples": {"image": {"content": {"image/*": {}}}}},
    ),
    current_user=Depends(oauth2.get_current_user),
):
    check_user_id_and_path_parameter(current_user.id, user_id)
    if not picture:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Provide a picture"
        )
    return user_service.upload_user_profile_picture(picture, current_user.id)


@router.get("/{user_id}/profile-picture")
def get_profile_picture_link(
    user_id: int = Path(...), db: Session = Depends(database.get_db)
):
    return user_service.get_profile_picture_link(user_id, db)


@router.delete("/{user_id}/profile-picture", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile_picture(
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    check_user_id_and_path_parameter(current_user.id, user_id)
    return user_service.delete_profile_picture(user_id, db)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int = Query(None),
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(oauth2.get_current_user),
):
    if user_id and not current_user.is_admin() and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User cannot delete another user.",
        )
    return user_service.delete_user(current_user.id if not user_id else user_id, db)


@router.get("/{user_id}/cars", response_model=List[CarDisplay], tags=["users", "cars"])
def read_cars_by_user(
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
):
    cars = car_service.get_cars_by_user(db, user_id)
    if not cars:
        raise HTTPException(status_code=404, detail="Cars not found for this user")
    return cars


@router.put(
    "/{user_id}/password",
    summary="Change password",
    description="This endpoint is used to change user's password.",
    status_code=status.HTTP_200_OK,
)
def change_password(
    new_password: str = Body(...),
    user_id: int = Path(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    check_user_id_and_path_parameter(current_user.id, user_id)
    return user_service.change_password(user_id, new_password, db)


@router.get(
    "/{user_id}/rentals",
    response_model=Dict[str, Union[Optional[int], Optional[List[RentalDisplay]]]],
    summary="Get user's rentals",
    description="This endpoint returns the rental of a given user.",
)
def get_user_rentals(
    user_id: int = Path(...),
    sort_by: RentalSort = Query(RentalSort.DATE),
    sort_dir: SortDirection = Query(SortDirection.ASC),
    skip: int = Query(0),
    limit: int = Query(constants.QUERY_LIMIT_DEFAULT),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    if not current_user.is_admin() and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User cannot query other user's rentals.",
        )

    return rental_service.get_rentals(
        db=db,
        current_user=current_user,
        sort_by=sort_by,
        sort_dir=sort_dir,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}/reviews",
    response_model=Dict[str, Union[Optional[int], Optional[List[ReviewDisplay]]]],
    summary="Get the reviews about a user",
    description="This endpoint returns the reviews about a user as a renter "
    "or as a owner of rentals",
)
def get_user_reviews(
    user_id: int = Path(...),
    sort_by: ReviewSort = Query(ReviewSort.REVIEW_DATE),
    sort_dir: SortDirection = Query(SortDirection.ASC),
    skip: int = Query(0),
    limit: int = Query(constants.QUERY_LIMIT_DEFAULT),
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    return review_service.get_views_by_user(
        db, user_id, current_user, sort_by, sort_dir, skip, limit
    )
