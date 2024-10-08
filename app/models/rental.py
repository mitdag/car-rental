from sqlalchemy import Column, Integer, ForeignKey, Float, Date, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.schemas.enums import RentalStatus


class DBRental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_id = Column(Integer, ForeignKey("cars.id"))
    renter_id = Column(Integer, ForeignKey("users.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(RentalStatus), default=RentalStatus.RESERVED, nullable=False)

    # Relationships
    car = relationship("DBCar", back_populates="rentals")
    renter = relationship("DBUser", back_populates="rentals")
    reviews = relationship("DBReview", back_populates="rental")
    # user = relationship(
    #     "DBUser", foreign_keys=[renter_id], back_populates="renter"
    # )
    # user = relationship(
    #     "DBUser", foreign_keys=[renter_id], back_populates="rental"
    # )
