from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class DBAddress(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    street = Column(String, default="")
    number = Column(String, default="")
    postal_code = Column(String, default="")
    city = Column(String, default="")
    state = Column(String, default="")
    country = Column(String, default="")
    latitude = Column(Float, default=None)
    longitude = Column(Float, default=None)
    is_address_confirmed = Column(Boolean, default=False)

    created_at = Column(DateTime)
    user = relationship("DBUser", back_populates="address")
