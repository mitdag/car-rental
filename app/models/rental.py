from  sqlalchemy import Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from app.core.database import Base


class DBRental(Base):
    __tablename__ = 'rentals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey('cars.id'))
    renter_id = Column(Integer, ForeignKey('users.id'))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    
    # Relationships
    car = relationship("DBCar", back_populates="rentals")
    renter = relationship("DBUser", back_populates="rentals")
    reviews = relationship("DBReview", back_populates="rental")
    
    