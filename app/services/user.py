import datetime
import uuid

from app.schemas.address import AddressProfile
from app.services.address import update_user_address
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from fastapi import status

from app.models.signup_confirmations import DBSignUpConfirmation
from app.models.user import DBUser
from app.schemas.enums import LoginMethod, UserType
from app.schemas.user import UserProfile
from app.utils.hash import Hash

CONFIRMATION_EXPIRE_PERIOD_IN_DAYS = 1


def create_signup_validation_entry(email: str, password: str, db: Session):
    user = db.query(DBUser).filter(email == DBUser.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user exists")

    new_confirmation = DBSignUpConfirmation(
        email=email,
        password=Hash.bcrypt(password),
        key=str(uuid.uuid4()),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=CONFIRMATION_EXPIRE_PERIOD_IN_DAYS)
    )
    db.add(new_confirmation)
    db.commit()
    db.flush(new_confirmation)
    return {"id": new_confirmation.id, "key": new_confirmation.key, "expires_in": CONFIRMATION_EXPIRE_PERIOD_IN_DAYS}


# This function is called via user confirmation email.
def create_signup_user_from_confirmation_mail(id: int, key: str, db: Session):
    confirmation = db.query(DBSignUpConfirmation).filter(id == DBSignUpConfirmation.id).first()
    if not confirmation:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No such user")

    confirmation_email = confirmation.email
    confirmation_password = confirmation.password
    db.delete(confirmation)
    db.commit()
    if confirmation.expires_at < datetime.datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Confirmation link expired")

    user = db.query(DBUser).filter(confirmation_email == DBUser.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exists")

    user = DBUser(
        email=confirmation_email,
        password=confirmation_password,
        login_method=LoginMethod.EMAIL,
        user_type=UserType.USER,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.flush(user)
    return {"email": user.email}


def modify_user_profile(user_profile: UserProfile, db: Session):
    user = db.query(DBUser).filter(user_profile.user_id == DBUser.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist.")

    user.name = user_profile.name
    user.last_name = user_profile.last_name
    user.phone_number = user_profile.phone_number

    db.add(user)
    db.commit()
    db.flush(user)

    update_user_address(
        user_id=user_profile.user_id,
        address_profile=AddressProfile(
            street=user_profile.street,
            number=user_profile.number,
            postal_code=user_profile.postal_code,
            city=user_profile.city,
            state=user_profile.state,
            country=user_profile.country
        ),
        db=db
    )
    return user_profile
