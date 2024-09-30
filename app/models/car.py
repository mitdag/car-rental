from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class DBCar(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    transmission_type = Column(String, nullable=False)
    motor_type = Column(String, nullable=False)
    price_per_day = Column(Float, nullable=False)
    description = Column(Text)
    is_listed = Column(Boolean, default=True)

    owner = relationship("DBUser", back_populates="cars")
    favorited_by = relationship(
        "DBUser", secondary="favorites", back_populates="user_favorites"
    )
    rentals = relationship("DBRental", back_populates="car")
