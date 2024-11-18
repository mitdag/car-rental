from fastapi import APIRouter, Body, Depends, status, Request, Query
from fastapi.responses import HTMLResponse
from pydantic import EmailStr

from sqlalchemy.orm import Session

import app.core.config
import app.services.user_auth_service
from app.auth.oauth2 import create_temp_confirmation_token, get_temp_user
from app.core import database
from app.schemas.enums import LoginMethod, UserType
from app.services import user as user_service

from app.utils import email_sender
from app.utils.constants import CONFIRMATION_EXPIRE_PERIOD_IN_DAYS
from app.utils.service_response import ServiceResponseStatus

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
        password: str = Body(...)
):
    token = create_temp_confirmation_token(
        {"email": email, "password": password}, CONFIRMATION_EXPIRE_PERIOD_IN_DAYS * 24 * 60)
    email_sender.send_signup_confirmation_email(
        receiver_address=email,
        path="http://127.0.0.1:8000/signup",
        params={"key": token},
        expires=CONFIRMATION_EXPIRE_PERIOD_IN_DAYS,
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
        key: str = Query(...),
        db: Session = Depends(database.get_db),
):
    signup_user = get_temp_user(key=key)
    response = user_service.create_new_user(
        signup_user.get("email"),
        signup_user.get("password"),
        LoginMethod.EMAIL,
        UserType.USER,
        True,
        db
    )
    if response.status == ServiceResponseStatus.SUCCESS:
        title = "Signup Completed"
        message = "Thank you for signing up. You can login and enjoy our app now!"
        status_code = status.HTTP_201_CREATED
    else:
        title = "Signup Failed"
        if response.status == ServiceResponseStatus.INTERNAL_SERVER_ERROR:
            message = f"Sorry, something went wrong. ({response.message}). Please try again"
        else:
            message = response.message
        status_code = response.status
    return app.core.config.templates.TemplateResponse(
        "request_confirmation.html",
        {"request": request, "title": title, "message": message},
        status_code=status_code,
    )
