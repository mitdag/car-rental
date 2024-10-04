from app.core.database import Base
from sqlalchemy import Column, String, DateTime

from _datetime import datetime


class DBRefreshToken(Base):
    __tablename__ = "refresh_token"
    email = Column(String, primary_key=True, unique=True, index=True)
    token = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow())
