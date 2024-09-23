from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import database
from app.schemas.user import UserBase, UserProfile

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post("/new")
def create_new_user(user: UserBase):
    return user



@router.post("/profile")
def modify_user_profile(user_profile: UserProfile, db: Session = Depends(database.get_db)):
    print(user_profile)