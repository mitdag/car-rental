from geopy.geocoders import Nominatim

# Initialize the Nominatim geocoder
geolocator = Nominatim(user_agent="car-rental")


def address_to_lat_lon(address: str):
    location = geolocator.geocode(address)
    if location:
        return {"lat": location.latitude, "long": location.longitude}
    else:
        return None


print(address_to_lat_lon("175 5th Avenue NYC"))
print(address_to_lat_lon("Merellaan, 2289EB, Rijswijk, ZH, Netherland"))