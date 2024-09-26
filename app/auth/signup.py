from fastapi import APIRouter, Depends, Body, status, Request, Query
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core import database
from app.schemas import user as user_schema
from app.services import user as user_service

from app.utils import email_sender

router = APIRouter(prefix="/signup", tags=["signup/login"])

templates = Jinja2Templates(directory="app/static/templates")


@router.post("/", response_model=user_schema.UserDisplay)
def signup(
        email: str = Body(...),
        password: str = Body(...),
        db: Session = Depends(database.get_db),
):
    entry = user_service.create_signup_validation_entry(email, password, db)
    email_sender.send_signup_confirmation_email(
        receiver_address=email,
        path="http://127.0.0.1:8000/signup/confirm",
        params={"key": entry["key"], "id": entry["id"]},
        expires=entry["expires_in"],
    )
    return Response(
        status_code=status.HTTP_200_OK, content="Confirmation mail has been sent"
    )


@router.get("/confirm", response_class=HTMLResponse)
def signup_confirmation(
        request: Request,
        confirmation_id: int = Query(...),
        key: str = Query(...),
        db: Session = Depends(database.get_db),
):
    result = user_service.create_signup_user_from_confirmation_mail(confirmation_id, key, db)
    if result["result"]:
        title = "Signup Completed"
        message = "Thank you for signing up. You can login and enjoy our app now!"
    else:
        title = "Signup Failed"
        message = f"Sorry, something went wrong. ({result['desc']}). Please try again"
    return templates.TemplateResponse(
        "signup_confirmation.html",
        {"request": request, "title": title, "message": message},
    )
