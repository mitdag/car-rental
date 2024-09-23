import datetime

from sqlalchemy.orm import Session

from app.models.address import DBAddress
from app.schemas.address import AddressProfile


def get_address_by_user_id(user_id: int, db: Session):
    return db.query(DBAddress).filter(user_id == DBAddress.user_id).first()


def update_user_address(user_id: int, address_profile: AddressProfile, db: Session):
    address = db.query(DBAddress).filter(DBAddress.user_id == user_id).first()
    if not address:
        db.delete(address)

    new_address = DBAddress(
        user_id=user_id,
        street_name=address_profile.street_name,
        number=address_profile.number,
        postal_code=address_profile.postal_code,
        city=address_profile.city,
        state=address_profile.state,
        country=address_profile.country,
        latitude=None,
        longitude=None,
        created_at=datetime.datetime.utcnow()
    )
