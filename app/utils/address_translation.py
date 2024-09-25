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
<<<<<<< HEAD
=======


# print(address_to_lat_lon("175 5th Avenue NYC"))
# print(address_to_lat_lon("q=102+Merellaan,+Rijswijk+Netherlands")) # "102 Merellaan Street, Rijswijk, Netherland"))


# {
#   "street": "70 Lange Kleiweg",
#   "postalcode": "2288GK",
#   "city": "Rijswijk",
#   "state": "ZH",
#   "country": "Netherlands"
# }
# ))
>>>>>>> 62d5304c3a0d622f0b8bfad986e3b07621fd51fd
