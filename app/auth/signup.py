from fastapi import APIRouter, Depends, Body, Query,status
from fastapi import Response
from sqlalchemy.orm import Session

from app.core import database
from app.schemas.user import UserDisplay
from app.services.user import create_signup_user_from_confirmation_mail, create_signup_validation_entry
from app.utils import email_sender

router = APIRouter(
    prefix="/signup",
    tags=["signup/login"]
)

@router.post("/", response_model=UserDisplay)
def signup(email: str = Body(...), password: str = Body(...), db: Session = Depends(database.get_db)):
    entry = create_signup_validation_entry(email, password, db)
    email_sender.send_signup_confirmation_email(
        receiver_address=email,
        path="http://127.0.0.1:8000/signup/confirm",
        params={"key": entry["key"], "id": entry["id"]},
        expires=entry["expires_in"]
    )
    return Response(status_code=status.HTTP_200_OK, content="Confirmation mail has been sent")


@router.get("/confirm")
def signup_confirmation(id: int= Query(...), key: str = Query(...), db: Session = Depends(database.get_db)):
    return Response(status_code=status.HTTP_200_OK, content=create_signup_user_from_confirmation_mail(id, key, db))

