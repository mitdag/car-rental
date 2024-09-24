from app.services import user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import database
#from app.schemas.user import UserBase, ReviewProfile

router = APIRouter(
    prefix="/review",
    tags=["review"]
)

@router.post("/profile")
def modify_user_profile( db: Session = Depends(database.get_db)):
    return user.modify_user_profile( db)