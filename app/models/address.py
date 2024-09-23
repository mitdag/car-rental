from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base



class DBAddress(Base):
    __tablename__="addresses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    street_name = Column(String)
    number = Column(String)
    postal_code = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime)
    user = relationship("DBUser", back_populates="address")