import datetime
import uuid

from fastapi import HTTPException
from sqlalchemy import and_

from sqlalchemy.orm import Session
from starlette import status

from app.models.fogot_password_confirmation import DBForgotPasswordConfirmation
from app.models.signup_confirmations import DBSignUpConfirmation
from app.models.user import DBUser
from app.schemas.enums import LoginMethod, UserType
from app.services.user import get_user_by_email
from app.utils.constants import CONFIRMATION_EXPIRE_PERIOD_IN_DAYS
from app.utils.hash import Hash


def create_signup_validation_entry(email: str, password: str, db: Session):
    user = db.query(DBUser).filter(email == DBUser.email).first()
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
    db.flush(new_confirmation)
    return {
        "id": new_confirmation.id,
        "expires_in": CONFIRMATION_EXPIRE_PERIOD_IN_DAYS,
    }


# This function is called via user confirmation email.
def create_signup_user_from_confirmation_mail(
    confirmation_id: int, key: str, db: Session
):
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist."
        )

    confirmation_email = confirmation.email
    confirmation_password = confirmation.password
    db.delete(confirmation)
    db.commit()
    if confirmation.expires_at < datetime.datetime.utcnow():
        return {"result": False, "desc": "Confirmation link expired"}

    user = db.query(DBUser).filter(confirmation_email == DBUser.email).first()
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
    db.flush(user)
    return {"result": True, "desc": user.email}


def create_social_media_signup_user(email: str, login_method: LoginMethod, db: Session):
    user = db.query(DBUser).filter(email == DBUser.email).first()
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
    db.flush(user)
    return {"result": True, "desc": user.email}


def update_user_login(email: str, db: Session):
    user = get_user_by_email(email, db)
    if user:
        user.last_login = datetime.datetime.now()
        db.commit()
    return user


def create_forgot_password_validation_entry(email: str, db: Session):
    user = db.query(DBUser).filter(email == DBUser.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No such user."
        )

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


def check_confirmation(confirm_id: int, key: str, db: Session):
    confirmation = (
        db.query(DBForgotPasswordConfirmation)
        .filter(
            and_(
                DBForgotPasswordConfirmation.id == confirm_id,
                DBForgotPasswordConfirmation.key == key,
            )
        )
        .first()
    )
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
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        return {
            "result": False,
            "message": "We could not confirm your account. Try creating a new account.",
        }
    return {"result": True, "user": user}


# This function is triggerd when the user clicks the change password link (email).
def check_change_password_link_validity(confirm_id: int, key: str, db: Session):
    is_valid_confirmation = check_confirmation(confirm_id, key, db)
    if not is_valid_confirmation["result"]:
        return is_valid_confirmation
    return check_user(is_valid_confirmation["email"], db)


# This function is triggerd when the user clicks the send button on change password form (browser).
def process_change_password(password: str, confirm_id: int, key: str, db: Session):
    is_valid_confirmation = check_confirmation(confirm_id, key, db)
    if not is_valid_confirmation["result"]:
        return is_valid_confirmation

    is_valid_user = check_user(is_valid_confirmation["email"], db)
    if not is_valid_user["result"]:
        return is_valid_user

    user = is_valid_user["user"]
    user.password = Hash.bcrypt(password)
    db.commit()
    db.flush(user)
    return {
        "result": True,
        "message": "Your password has been successfully changed. Please proceed to login.",
    }
