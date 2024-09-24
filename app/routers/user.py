from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import database
from app.schemas.user import UserProfile
from app.services import user

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/profile")
def modify_user_profile(
    user_profile: UserProfile, db: Session = Depends(database.get_db)
):
    return user.modify_user_profile(user_profile, db)
