import datetime
import uuid

from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.signup_confirmations import DBSignUpConfirmation
from app.models.user import DBUser
from app.schemas.address import AddressDisplay
from app.schemas.enums import LoginMethod, UserType
from app.schemas.user import UserProfileForm
from app.services import address as address_service
from app.utils.hash import Hash

CONFIRMATION_EXPIRE_PERIOD_IN_DAYS = 1


def get_user_by_id(user_id: int, db: Session):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    # user = db.query(DBUser).options(joinedload(DBUser.cars)).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )
    return user


def get_user_by_email(email: str, db: Session):
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist."
        )
    return user


def get_users(db: Session, skip: int, limit: int = 20):
    if skip < 0 or limit < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skip and limit must be positive integers",
        )
    result = db.query(DBUser).offset(skip).limit(limit).all()
    return {
        "next_offset": (skip + limit) if len(result) == limit else None,
        "users": result,
    }


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
        "key": new_confirmation.key,
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


def modify_user_profile(user_id: int, user_profile: UserProfileForm, db: Session):
    user = db.query(DBUser).filter(user_id == DBUser.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist."
        )

    user.name = user_profile.name
    user.last_name = user_profile.last_name
    user.phone_number = user_profile.phone_number

    db.add(user)
    db.commit()
    db.flush(user)

    address_profile = address_service.update_user_address(
        user_id=user_id,
        address_profile=AddressDisplay(
            street=user_profile.street,
            number=user_profile.number,
            postal_code=user_profile.postal_code,
            city=user_profile.city,
            state=user_profile.state,
            country=user_profile.country,
        ),
        db=db,
    )
    return {
        "profile": user_profile,
        "address_confirmed": (address_profile.latitude and address_profile.longitude)
        is not None,
    }


def delete_user(user_id: int, db: Session):
    user = db.query(DBUser).filter(user_id == DBUser.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist."
        )

    db.delete(user)
    db.commit()
    return "Deleted"


def is_user_profile_complete(user_id, db):
    user = db.query(DBUser).filter(user_id == DBUser.id).first()
    if not user:
        return False
    else:
        return (
            user.phone_number != ""
            and user.is_verified
            and address_service.is_user_address_complete(user_id, db)
        )


def update_user_login(email: str, db: Session):
    user = get_user_by_email(email, db)
    if user:
        user.last_login = datetime.datetime.now()
        db.commit()
    return user
