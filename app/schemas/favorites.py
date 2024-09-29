from pydantic import BaseModel


class FavoritesBase(BaseModel):
    user_id: int
    car_id: int

    class Config:
        from_attributes = True
