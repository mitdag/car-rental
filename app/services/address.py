from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.address import DBAddress
from app.models.user import DBUser
from app.schemas.address import (
    AddressForm,
    AddressUpdate,
    create_address_private_display,
)
from app.utils.logger import logger


def get_address_by_user_id(user_id: int, db: Session):
    address = db.query(DBAddress).filter(user_id == DBAddress.user_id).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No address for the user"
        )
    return address


def update_user_address(user: DBUser, address_update: AddressUpdate, db: Session):
    db_address = db.query(DBAddress).filter(DBAddress.user_id == user.id).first()
    if db_address:
        # Convert AddressUpdate to AddressForm which has latitude and longitude
        update_data = AddressForm(
            **address_update.model_dump(exclude_unset=True)
        ).model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_address, key, value)

        try:
            db.add(db_address)
            db.commit()
            db.refresh(db_address)
        except Exception as exc:
            logger.error(exc)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while updating the address: {str(exc)}",
            )
    # If address doesnt exist before create new
    else:
        # Raises error if it cant generate coordinates
        new_address = AddressForm(**address_update.model_dump(exclude_unset=True))

        try:
            db_new_address = DBAddress(**new_address.model_dump(), user_id=user.id)
            db.add(db_new_address)
            db.commit()
            db.flush(db_new_address)
        except Exception as exc:
            logger.error(exc)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while updating the address: {str(exc)}",
            )
    return create_address_private_display(user)


def delete_user_address(user_id: int, db: Session):
    address = db.query(DBAddress).filter(user_id == DBAddress.user_id).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No address for the user"
        )
    db.delete(address)
    db.commit()
    return "deleted"


def is_user_address_complete(user_id, db):
    address = db.query(DBAddress).filter(user_id == DBAddress.user_id).first()
    if not address:
        return False
    return address.latitude is not None
