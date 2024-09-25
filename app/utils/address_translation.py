from typing import Dict

from geopy.geocoders import Nominatim

from app.utils.logger import logger

geolocator = Nominatim(user_agent="car-rental", timeout=3)


def address_to_lat_lon(address: Dict):
    try:
        location = geolocator.geocode(address)
        if location:
            return {"latitude": location.latitude, "longitude": location.longitude}
        else:
            return {"latitude": None, "longitude": None}
    except Exception as exc:
        logger.error(exc)
        return {"latitude": None, "longitude": None}
