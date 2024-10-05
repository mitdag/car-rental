from fastapi import APIRouter, Body, Depends, status, Request, Query
from fastapi.responses import HTMLResponse
from pydantic import EmailStr

from sqlalchemy.orm import Session

import app.core.config
import app.services.user_auth_service
from app.core import database


from app.utils import email_sender

router = APIRouter(prefix="/signup", tags=["auth-signup"])


@router.post(
    "",
    summary="Start a 'signup with email' process",
    description="This endpoint used for the users who want to signup by using their email. "
    "Signup process does not end at this endpoint. link to the provided email address."
    "Users who want to signup with social media accounts use login endpoint.",
)
def signup(
    email: EmailStr = Body(...),
    password: str = Body(...),
    db: Session = Depends(database.get_db),
):
    entry = app.services.user_auth_service.create_signup_validation_entry(
        email, password, db
    )
    email_sender.send_signup_confirmation_email(
        receiver_address=email,
        path="http://127.0.0.1:8000/signup",
        params={"key": entry["key"], "confirmation_id": entry["id"]},
        expires=entry["expires_in"],
    )
    return {
        "status_code": status.HTTP_200_OK,
        "content": "Confirmation email has been sent",
    }


@router.get(
    "",
    response_class=HTMLResponse,
    summary="Finalize the 'signup with email' process",
    description="This endpoint is triggered when the user clicks the signup confirmation "
    "link in the email. It returns an html code to inform the user about the "
    "success/failure of the signup process.",
)
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
