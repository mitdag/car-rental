from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class DBReview(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rental_id = Column(Integer, ForeignKey('rentals.id'))
    reviewer_id = Column(Integer, ForeignKey('users.id')) 
    reviewee_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Integer, nullable=False)
    comment = Column(String)
    review_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rental = relationship("DBRental", back_populates="reviews")
    reviewer = relationship("DBUser", foreign_keys=[reviewer_id], back_populates="reviews_written")
    reviewee = relationship("DBUser", foreign_keys=[reviewee_id], back_populates="reviews_received")