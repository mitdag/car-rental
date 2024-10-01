from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

from app.core.database import Base


class DBForgotPasswordConfirmation(Base):
    __tablename__ = "forgot_pass_confirmations"
    id = Column(Integer, primary_key=True, unique=True)
    email = Column(String)
    key = Column(String)
    expires_at = Column(DateTime)

    def is_key_alive(self):
        return datetime.utcnow() < self.expires_at
