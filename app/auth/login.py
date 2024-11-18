from typing_extensions import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse

import app.core.config
from app.auth.oauth2 import create_temp_confirmation_token, get_temp_user
from app.models.refresh_token import DBRefreshToken
from app.services import user_auth_service
from app.auth import oauth2
from app.core import database
from app.schemas.enums import LoginMethod
from app.services import user as user_service
from app.utils import email_sender
from app.utils.constants import CONFIRMATION_EXPIRE_PERIOD_IN_DAYS
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
    "/forgotten-password",
    summary="Start a 'Forgot password' process",
    description="This endpoint is triggerd when the user clicks 'Forgot password' button. The provided "
                "password is checked if the user really has an account. If so, an change password link "
                "is sent to user's email.",
)
def forgot_password(
        request: Request, email: str, db: Session = Depends(database.get_db)
):
    if not user_service.get_user_by_email(email, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such user")
    expires_in = CONFIRMATION_EXPIRE_PERIOD_IN_DAYS * 24 * 60
    token = create_temp_confirmation_token(
        data={"email": email},
        expire_minutes=expires_in
    )
    email_sender.send_forgot_password_email(
        receiver_address=email,
        path=f"{request.base_url}login/password-form",
        params={"key": token},
        expires=CONFIRMATION_EXPIRE_PERIOD_IN_DAYS
    )
    return {
        "status_code": status.HTTP_200_OK,
        "content": "Change password email has been sent",
    }


@router.get(
    "/password-form",
    response_class=HTMLResponse,
    summary="Request reset password form",
    description="This endpoint is triggerd when the user clicks the reset password link in the email. "
                "If the link in the email is valid then change_password.html is returned. Else a fail "
                "message is sent by returning request_confirmation.html",
)
def reset_password(
        request: Request,
        key: str = Query(...),
):
    try:
        tmp_user = get_temp_user(key)
        if not tmp_user or not tmp_user.get("email"):
            raise Exception()
        else:
            return app.core.config.templates.TemplateResponse(
                "change_password.html",
                {
                    "request": request,
                    "title": "Change Password",
                    "key": key,
                },
                status_code=status.HTTP_200_OK,
            )
    except Exception:
        return app.core.config.templates.TemplateResponse(
            "request_confirmation.html",
            {
                "request": request,
                "title": "Change Password Failed",
                "message": "We could not confirm your request (link might have expired))",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


@router.post(
    "/password-form",
    response_class=HTMLResponse,
    summary="Send reset password form",
    description="This endpoint is triggerd when the user clicks the send button on 'reset password' form (browser). "
                "Returns request_confirmation.html",
)
def reset_password_confirmation(
        request: Request,
        password: Annotated[str, Form()],
        key: Annotated[str, Form()],
        db: Session = Depends(database.get_db),
):
    title = ""
    message = ""
    status_code = 0
    try:
        tmp_user = get_temp_user(key)
        if not tmp_user or not tmp_user.get("email"):
            raise Exception()
        result = user_auth_service.reset_change_password(email=tmp_user.get("email"), password=password, db=db)

        if result["result"]:
            title = "Password changed"
            message = result["message"]
            status_code = status.HTTP_201_CREATED
        else:
            title = "Password Change Failed"
            message = result["message"]
            status_code = status.HTTP_401_UNAUTHORIZED
    except Exception:
        title = "Password Change Failed"
        message = "Link expired"
        status_code = status.HTTP_401_UNAUTHORIZED
    finally:
        return app.core.config.templates.TemplateResponse(
            "request_confirmation.html",
            {"request": request, "title": title, "message": message},
            status_code=status_code,
        )


@router.post("/refresh-token")
def refresh_key(
        current_user=Depends(oauth2.get_current_user_refresh_key),
        db=Depends(database.get_db),
):
    user, token = current_user
    db_token = (
        db.query(DBRefreshToken).filter(DBRefreshToken.email == user.email).first()
    )
    # At this point access_token provided by the user is valid (i.e. it was issued by this application) and
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
