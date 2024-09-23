import datetime

from pydantic import BaseModel


def set_lat_long(**data):
    street_name, \
        number, \
        postal_code, \
        city, \
        state, \
        country = data

    return {"latitude": 0, "longitude": 0}


class AddressBase(BaseModel):
    street_name: str
    number: str
    postal_code: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float

    def __init__(self, **data):
        lat_long = set_lat_long(**data)
        data["latitude"] = lat_long["latitude"]
        data["longitude"] = lat_long["latitude"]

        super().__init__(**data)


class AddressProfile(BaseModel):
    street_name: str
    number: str
    postal_code: str
    city: str
    state: str
    country: str
