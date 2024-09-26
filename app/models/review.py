from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class DBReview(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    #rental_id = Column(Integer, ForeignKey("rentals.rental_id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    reviewee_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(String)
    review_date = Column(DateTime, default=datetime.utcnow)  # Set a default value if needed

    # Relationships
    #rental = relationship("Rental", back_populates="reviews")  # Adjust as necessary
    reviewer = relationship("DBUser", foreign_keys=[reviewer_id])  # Adjust as necessary
    reviewee = relationship("DBUser", foreign_keys=[reviewee_id])  # Adjust as necessary