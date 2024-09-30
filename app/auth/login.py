from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import oauth2
from app.core import database
from app.schemas.enums import LoginMethod
from app.services import user as user_service
from app.utils.hash import Hash
from app.utils.logger import logger

router = APIRouter(prefix="/login", tags=["signup/login"])


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


@router.post("/")
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
            user_service.create_social_media_signup_user(
                auth_form.username, login_method, db
            )

    access_token = oauth2.create_access_token({"username": auth_form.username})
    user_service.update_user_login(auth_form.username, db)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": f"{auth_form.username}",
    }
