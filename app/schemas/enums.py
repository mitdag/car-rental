from enum import Enum


class LoginMethod(str, Enum):
    EMAIL = "EMAIL"
    FACEBOOK = "FACEBOOK"
    GOOGLE = "GOOGLE"
    APPLE = "APPLE"


class UserType(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class CarEngineType(str, Enum):
    GASOLINE = "GASOLINE"
    DIESEL = "DIESEL"
    ELECTRIC = "ELECTRIC"
    HYBRID = "HYBRID"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class CarTransmissionType(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class CarSearchSortType(str, Enum):
    DISTANCE = "DISTANCE"
    ENGINE_TYPE = "ENGINE_TYPE"
    TRANSMISSION_TYPE = "TRANSMISSION_TYPE"
    PRICE = "PRICE"
    MAKE = "MAKE"


class CarSearchSortDirection(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class RentalStatus(str, Enum):
    # When the start time of the rental is in the future
    RESERVED = "RESERVED"

    # The car is in renter's usage (in rental period)
    BOOKED = "BOOKED"

    # Car is returned by the renter (end of rental period)
    RETURNED = "RETURNED"

    # Reservation is cancelled by the renter or the owner
    CANCELLED = "CANCELLED"
