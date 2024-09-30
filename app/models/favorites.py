from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey


class DBFavorite(Base):
    __tablename__ = "favorites"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    car_id = Column(Integer, ForeignKey("cars.id"), primary_key=True)
