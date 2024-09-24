import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.schemas.enums import LoginMethod, UserType


class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="")
    last_name = Column(String, default="")
    email = Column(String, unique=True, index=True)
    password = Column(String, default="")
    login_method = Column(SqlEnum(LoginMethod))
    phone_number = Column(String, default="")
    user_type = Column(SqlEnum(UserType))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow())
    last_login = Column(DateTime, default=None)
    address = relationship("DBAddress", back_populates="user")
    cars = relationship("DBCar", back_populates="user")
