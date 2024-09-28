from enum import Enum


class LoginMethod(Enum):
    EMAIL = 1
    FACEBOOK = 2
    GOOGLE = 3
    APPLE = 4


class UserType(Enum):
    USER = 1
    ADMIN = 2


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
