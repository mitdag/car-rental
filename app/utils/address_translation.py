from typing import Dict

from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="car-rental", timeout=3)


def address_to_lat_lon(address: Dict):
    location = geolocator.geocode(address)
    if location:
        return {"latitude": location.latitude, "longitude": location.longitude}
    else:
        return {"latitude": None, "longitude": None}


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
