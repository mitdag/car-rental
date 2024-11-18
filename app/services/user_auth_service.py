import datetime

from sqlalchemy.orm import Session

from app.models.refresh_token import DBRefreshToken
from app.models.user import DBUser
from app.schemas.enums import LoginMethod, UserType
from app.services import user as user_service

from app.utils.hash import Hash


def create_social_media_signup_user(email: str, login_method: LoginMethod, db: Session):
    user = user_service.get_user_by_email(email, db)
    if user:
        return {"result": False, "desc": "User already exists"}

    user = DBUser(
        email=email,
        password=None,
        login_method=login_method,
        user_type=UserType.USER,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"result": True, "desc": user.email}


def update_user_login(email: str, db: Session):
    user = user_service.get_user_by_email(email, db)
    if user:
        user.last_login = datetime.datetime.now()
        db.commit()
    return user


def reset_change_password(email: str, password: str, db: Session):
    user = user_service.get_user_by_email(email, db)
    if not user:
        return {
            "result": False,
            "message": "No such user",
        }
    user.password = Hash.bcrypt(password.strip())
    db.commit()
    db.refresh(user)
    return {
        "result": True,
        "message": "Your password has been successfully changed. Please proceed to login.",
    }


def save_refresh_token(user_email: str, token: str, db: Session):
    if db.query(DBRefreshToken).filter(DBRefreshToken.email == user_email).first():
        return False
    new_token = DBRefreshToken()
    new_token.email = user_email
    new_token.token = Hash.bcrypt(token)
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    return new_token


def revoke_refresh_token(user_email: str, db: Session):
    token = db.query(DBRefreshToken).filter(DBRefreshToken.email == user_email).first()
    if token:
        db.delete(token)
        db.commit()
