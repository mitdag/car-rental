from fastapi import APIRouter, Depends, Body, status, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

import app.core.config
import app.services.user_auth_service
from app.core import database

from app.utils import email_sender

router = APIRouter(prefix="/signup", tags=["signup/login"])


@router.post("/")
def signup(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(database.get_db),
):
    entry = app.services.user_auth_service.create_signup_validation_entry(
        email, password, db
    )
    email_sender.send_signup_confirmation_email(
        receiver_address=email,
        path="http://127.0.0.1:8000/signup/confirm",
        params={"key": entry["key"], "confirmation_id": entry["id"]},
        expires=entry["expires_in"],
    )
    return {
        "status_code": status.HTTP_200_OK,
        "content": "Confirmation email has been sent",
    }


@router.get("/confirm", response_class=HTMLResponse)
def signup_confirmation(
    request: Request,
    confirmation_id: int = Query(...),
    key: str = Query(...),
    db: Session = Depends(database.get_db),
):
    result = app.services.user_auth_service.create_signup_user_from_confirmation_mail(
        confirmation_id, key, db
    )
    if result["result"]:
        title = "Signup Completed"
        message = "Thank you for signing up. You can login and enjoy our app now!"
    else:
        title = "Signup Failed"
        message = f"Sorry, something went wrong. ({result['desc']}). Please try again"
    return app.core.config.templates.TemplateResponse(
        "request_confirmation.html",
        {"request": request, "title": title, "message": message},
    )
