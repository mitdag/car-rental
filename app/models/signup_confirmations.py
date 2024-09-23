from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime


class DBSignUpConfirmation(Base):
    __tablename__="signup_confirmations"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String)
    key = Column(String)
    expires_at = Column(DateTime)