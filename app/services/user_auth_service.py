import datetime
import uuid

from fastapi import HTTPException
from sqlalchemy import and_

from sqlalchemy.orm import Session
from starlette import status

from app.models.fogot_password_confirmation import DBForgotPasswordConfirmation
from app.models.refresh_token import DBRefreshToken
from app.models.signup_confirmations import DBSignUpConfirmation
from app.models.user import DBUser
from app.schemas.enums import LoginMethod, UserType
from app.services import user as user_service
from app.utils.constants import CONFIRMATION_EXPIRE_PERIOD_IN_DAYS
from app.utils.hash import Hash


def create_signup_validation_entry(email: str, password: str, db: Session):
    user = user_service.get_user_by_email(email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    new_confirmation = DBSignUpConfirmation(
        email=email,
        password=Hash.bcrypt(password),
        key=str(uuid.uuid4()),
        expires_at=datetime.datetime.utcnow()
        + datetime.timedelta(days=CONFIRMATION_EXPIRE_PERIOD_IN_DAYS),
    )
    db.add(new_confirmation)
    db.commit()
    db.refresh(new_confirmation)
    return {
        "id": new_confirmation.id,
        "key": new_confirmation.key,
        "expires_in": CONFIRMATION_EXPIRE_PERIOD_IN_DAYS,
    }


# This function is called via user confirmation email.
def create_signup_user_from_confirmation_mail(confirmation_id: int, key: str, db):
    confirmation = (
        db.query(DBSignUpConfirmation)
        .filter(
            and_(
                confirmation_id == DBSignUpConfirmation.id,
                key == DBSignUpConfirmation.key,
            )
        )
        .first()
    )
    if not confirmation:
        return {"result": False, "desc": "Invalid signup"}

    confirmation_email = confirmation.email
    confirmation_password = confirmation.password
    db.delete(confirmation)
    db.commit()
    if confirmation.expires_at < datetime.datetime.utcnow():
        return {"result": False, "desc": "Confirmation link expired"}

    user = user_service.get_user_by_email(confirmation_email, db)
    if user:
        return {"result": False, "desc": "User already exists"}

    user = DBUser(
        email=confirmation_email,
        password=confirmation_password,
        login_method=LoginMethod.EMAIL,
        user_type=UserType.USER,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"result": True, "desc": user.email}


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


def create_forgot_password_validation_entry(email: str, db: Session):
    user = user_service.get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No such user."
        )

    # delete old reset password request (if any) by this user
    old_confirmation = (
        db.query(DBForgotPasswordConfirmation)
        .filter(email == DBForgotPasswordConfirmation.email)
        .first()
    )
    if old_confirmation:
        db.delete(old_confirmation)
        db.commit()

    uuid_key = str(uuid.uuid4())
    new_confirmation = DBForgotPasswordConfirmation(
        email=email,
        key=uuid_key,
        expires_at=datetime.datetime.utcnow()
        + datetime.timedelta(days=CONFIRMATION_EXPIRE_PERIOD_IN_DAYS),
    )
    db.add(new_confirmation)
    db.commit()
    db.flush(new_confirmation)
    return {
        "id": new_confirmation.id,
        "key": uuid_key,
        "expires_in": CONFIRMATION_EXPIRE_PERIOD_IN_DAYS,
    }


def check_forgot_password_confirmation(confirm_id: int, key: str, db: Session):
    confirmation = get_forgot_password_confirmation(confirm_id, key, db)

    if not confirmation:
        return {
            "result": False,
            "message": "We could not confirm your password change request. Please try making another change request.",
        }
    if not confirmation.is_key_alive():
        return {
            "result": False,
            "message": "Confirmation key expired. Please make a new change password request.",
        }
    return {"result": True, "email": confirmation.email}


def check_user(email: str, db):
    user = user_service.get_user_by_email(email, db)
    if not user:
        return {
            "result": False,
            "message": "We could not confirm your account. Try creating a new account.",
        }
    return {"result": True, "user": user}


def get_forgot_password_confirmation(confirmation_id: int, key: str, db: Session):
    return (
        db.query(DBForgotPasswordConfirmation)
        .filter(
            and_(
                DBForgotPasswordConfirmation.id == confirmation_id,
                DBForgotPasswordConfirmation.key == key,
            )
        )
        .first()
    )


def delete_forgot_password_confirmation(confirmation_id, key, db):
    confirmation = get_forgot_password_confirmation(confirmation_id, key, db)
    if confirmation:
        db.delete(confirmation)
        db.commit()


# This function is triggerd when the user clicks the change password link (email).
def check_change_password_link_validity(confirm_id: int, key: str, db: Session):
    is_valid_confirmation = check_forgot_password_confirmation(confirm_id, key, db)
    if not is_valid_confirmation["result"]:
        return is_valid_confirmation
    return check_user(is_valid_confirmation["email"], db)


# This function is triggerd when the user clicks the send button on change password form (browser).
def reset_change_password(password: str, confirm_id: int, key: str, db: Session):
    is_valid_confirmation = check_forgot_password_confirmation(confirm_id, key, db)
    if not is_valid_confirmation["result"]:
        return is_valid_confirmation

    is_valid_user = check_user(is_valid_confirmation["email"], db)
    if not is_valid_user["result"]:
        return is_valid_user

    if not password or password.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty password"
        )
    user = is_valid_user["user"]
    user.password = Hash.bcrypt(password.strip())
    db.commit()
    db.flush(user)
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
    db.flush(new_token)

    return True


def revoke_refresh_token(user_email: str, db: Session):
    token = db.query(DBRefreshToken).filter(DBRefreshToken.email == user_email).first()
    if token:
        db.delete(token)
        db.commit()


def verify_refresh_token(user_email: str, token: str, db: Session):
    db_token = (
        db.query(DBRefreshToken).filter(DBRefreshToken.email == user_email).first()
    )
    if not db_token:
        return False
