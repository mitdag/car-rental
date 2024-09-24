import datetime

from sqlalchemy.orm import Session

from app.models.address import DBAddress
from app.schemas.address import AddressProfile
from app.utils.address_translation import address_to_lat_lon


def get_address_by_user_id(user_id: int, db: Session):
    return db.query(DBAddress).filter(user_id == DBAddress.user_id).first()


def update_user_address(user_id: int, address_profile: AddressProfile, db: Session):
    address = db.query(DBAddress).filter(DBAddress.user_id == user_id).first()
    if address:
        db.delete(address)
    lat_long = address_to_lat_lon(
        {
            "street": f"{address_profile.number} {address_profile.street}",
            "postalcode": address_profile.postal_code,
            "city": address_profile.city,
            "state": address_profile.state,
            "country": address_profile.country,
        }
    )
    new_address = DBAddress(
        user_id=user_id,
        street=address_profile.street,
        number=address_profile.number,
        postal_code=address_profile.postal_code,
        city=address_profile.city,
        state=address_profile.state,
        country=address_profile.country,
        latitude=lat_long["latitude"],
        longitude=lat_long["longitude"],
        created_at=datetime.datetime.utcnow(),
    )
    db.add(new_address)
    db.commit()
    db.flush(new_address)


def delete_user_address(user_id: int, db: Session):
    address = db.query(DBAddress).filter(user_id == DBAddress.user_id).first()
    if address:
        db.delete(address)
        db.commit()
        return "deleted"
    return "No address for the user"
