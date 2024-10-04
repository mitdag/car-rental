from typing import Dict

from geopy.geocoders import Nominatim

from app.utils.logger import logger

geolocator = Nominatim(user_agent="car-rental", timeout=3)


class AddressValidationError(Exception):
    pass


def address_to_lat_lon(address: Dict):
    try:
        location = geolocator.geocode(address)
        if location:
            return {"latitude": location.latitude, "longitude": location.longitude}
        else:
            raise AddressValidationError("Invalid address: unable to geocode.")
    except Exception as exc:
        logger.error(exc)
        raise AddressValidationError(f"Error occurred during geocoding: {exc}")
