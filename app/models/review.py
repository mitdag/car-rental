from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class DBReview(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.rental_id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    reviewee_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    review_date = Column(DateTime, default=datetime.utcnow)

    rental = relationship("Rental", back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    reviewee = relationship("User", foreign_keys=[reviewee_id])