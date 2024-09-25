from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Review(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey('rentals.rental_id'))
    reviewer_id = Column(Integer, ForeignKey('users.user_id'))
    reviewee_id = Column(Integer, ForeignKey('users.user_id'))
    rating = Column(Integer)
    comment = Column(String)
    review_date = Column(DateTime, default=datetime.utcnow)

    rental = relationship("Rental", back_populates="reviews")