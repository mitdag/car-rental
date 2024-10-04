from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core import database
from app.models.user import DBUser
from app.services import user_auth_service

router = APIRouter(prefix="/logout", tags=["auth"])


@router.post(
    "", summary="Logout", description="Refresh tokens is revoked (deleted from db)."
)
def logout(
    db: Session = Depends(database.get_db),
    current_user: DBUser = Depends(oauth2.get_current_user),
):
    user_auth_service.revoke_refresh_token(current_user.email, db)
    return "logged out"
