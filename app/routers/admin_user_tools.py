from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.models.user import DBUser
from app.schemas.user import UserDisplay, UserProfileForm

from app.services import user as user_service

router = APIRouter(prefix="/admin", tags=["admin user tools"])


@router.delete(
    "/users/{user_id}",
    summary="Delete a user",
    description="Endpoint for admin to delete a user",
)
def delete_user(
    user_id: int = Path(...),
    admin: DBUser = Depends(oauth2.admin_only),
    db: Session = Depends(database.get_db),
):
    return user_service.delete_user(user_id, db)


@router.get(
    "/users/{user_id}",
    response_model=UserDisplay,
    summary="Get user details",
    description="Endpoint for admin to get user details",
)
def get_user(
    user_id: int = Path(...),
    admin: DBUser = Depends(oauth2.admin_only),
    db: Session = Depends(database.get_db),
):
    return user_service.get_user_by_id(user_id, db)


@router.put(
    "/users/{user_id}",
    response_model=UserDisplay,
    summary="Edit a user",
    description="Endpoint for admin to edit a user",
)
def modify_user(
    user_profile: UserProfileForm,
    user_id: int = Path(...),
    admin: DBUser = Depends(oauth2.admin_only),
    db: Session = Depends(database.get_db),
):
    return user_service.modify_user(user_id, user_profile, db)
