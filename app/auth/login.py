from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse

import app.core.config
from app.models.refresh_token import DBRefreshToken
from app.services import user_auth_service
from app.auth import oauth2
from app.core import database
from app.schemas.enums import LoginMethod
from app.services import user as user_service
from app.utils import email_sender
from app.utils.hash import Hash
from app.utils.logger import logger

router = APIRouter(prefix="/login", tags=["auth-login"])


class OAuth2PasswordRequestFormCustom(OAuth2PasswordRequestForm):
    def __init__(
        self,
        login_method: LoginMethod = Form(
            LoginMethod.EMAIL
        ),  # Expecting login_method as form input
        username: str = Form(...),
        password: str = Form(None),
    ):
        super().__init__(username=username, password=password)
        self.login_method = login_method


@router.post(
    "",
    summary="Login for email users, signup/login for social media users.",
    description="Users can login and get a token from via this endpoint. "
    "If the user is a social media user and if has no account yet "
    "a new account is also created and access token provided at this endpoint.",
)
def login(
    auth_form: OAuth2PasswordRequestFormCustom = Depends(),
    db: Session = Depends(database.get_db),
):
    # TODO following line is for demo purposes on Swagger. login_method will be sent by backend
    # login_method = auth_form.login_method
    # login_method = LoginMethod.EMAIL if auth_form.password != "LOGIN_WITH_SOCIAL_MEDIA" \
    #     else LoginMethod(auth_form.login_method)
    login_method = (
        LoginMethod.EMAIL
        if not auth_form.login_method
        else LoginMethod(auth_form.login_method)
    )
    if login_method == LoginMethod.EMAIL:
        if not auth_form.password or auth_form.password == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.No password",
            )

        try:
            app_user = user_service.get_user_by_email(auth_form.username, db)
            if not app_user or not Hash.verify(auth_form.password, app_user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )
        except Exception:
            logger.error(
                f"Login attempt with invalid credentials ({auth_form.username})"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
            )
    else:
        user = user_service.get_user_by_email(auth_form.username, db)
        if not user:
            user_auth_service.create_social_media_signup_user(
                auth_form.username, login_method, db
            )

    access_token, refresh_token = oauth2.create_tokens({"username": auth_form.username})
    user_auth_service.revoke_refresh_token(auth_form.username, db)
    user_auth_service.save_refresh_token(auth_form.username, refresh_token, db)
    user_auth_service.update_user_login(auth_form.username, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": f"{auth_form.username}",
    }


@router.post(
    "/forgot-password",
    summary="Start a 'Forgot password' process",
    description="This endpoint is triggerd when the user clicks 'Forgot password' button. The provided "
    "password is checked if the user really has an account. If so, an change password link "
    "is sent to user's email.",
)
def forgot_password(email: str, db: Session = Depends(database.get_db)):
    entry = user_auth_service.create_forgot_password_validation_entry(email, db)
    email_sender.send_forgot_password_email(
        receiver_address=email,
        path="http://127.0.0.1:8000/login/password-form",
        params={"key": entry["key"], "confirm_id": entry["id"]},
        expires=entry["expires_in"],
    )
    return {
        "status_code": status.HTTP_200_OK,
        "content": "Change password email has been sent",
    }


@router.get(
    "/password-form",
    response_class=HTMLResponse,
    summary="Request change password form",
    description="This endpoint is triggerd when the user clicks the reset password link in the email.",
)
def reset_password(
    request: Request,
    confirm_id: int = Query(...),
    key: str = Query(...),
    db: Session = Depends(database.get_db),
):
    result = user_auth_service.check_change_password_link_validity(confirm_id, key, db)
    user_auth_service.delete_forgot_password_confirmation(confirm_id, key, db)
    if result["result"]:
        return app.core.config.templates.TemplateResponse(
            "change_password.html",
            {
                "request": request,
                "title": "Change Password",
                "confirm_id": confirm_id,
                "key": key,
            },
        )
    return app.core.config.templates.TemplateResponse(
        "request_confirmation.html",
        {
            "request": request,
            "title": "Change Password Failed",
            "message": result["message"],
        },
    )


@router.post(
    "/password-form",
    response_class=HTMLResponse,
    summary="Send reset password form",
    description="This endpoint is triggerd when the user clicks the send button on 'reset password' form (browser).",
)
def reset_password_confirmation(
    request: Request,
    password: Annotated[str, Form()],
    confirm_id: Annotated[int, Form()],
    key: Annotated[str, Form()],
    db: Session = Depends(database.get_db),
):
    result = user_auth_service.reset_change_password(password, confirm_id, key, db)
    if result["result"]:
        title = "Password changed"
        message = result["message"]
    else:
        title = "Password Change Failed"
        message = result["message"]
    return app.core.config.templates.TemplateResponse(
        "request_confirmation.html",
        {"request": request, "title": title, "message": message},
    )


@router.post("/refresh")
def refresh_key(
    current_user=Depends(oauth2.get_current_user_refresh_key),
    db: Session = Depends(database.get_db),
):
    user, token = current_user
    db_token = db.query(DBRefreshToken).filter(DBRefreshToken.email == user.email)
    # At this point access_token provided by the user is valid (i.e. it was issued by this application and
    # it has not expired yet. However, we should make sure that the user did not revoke it (i.e. logged out)
    # in the past. Thus, it must be in our db.
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorised."
        )
    access_token, refresh_token = oauth2.create_tokens({"username": user.email})
    user_auth_service.revoke_refresh_token(user.email, db)
    user_auth_service.save_refresh_token(user.email, refresh_token, db)
    user_auth_service.update_user_login(user.email, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": f"{user.email}",
    }
