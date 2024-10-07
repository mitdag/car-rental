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


class CarMake(str, Enum):
    ACURA = "Acura"
    ALFA_ROMEO = "Alfa Romeo"
    ASTON_MARTIN = "Aston Martin"
    AUDI = "Audi"
    BENTLEY = "Bentley"
    BMW = "BMW"
    BUGATTI = "Bugatti"
    BUICK = "Buick"
    CADILLAC = "Cadillac"
    CHEVROLET = "Chevrolet"
    CHRYSLER = "Chrysler"
    CITROEN = "Citroen"
    DODGE = "Dodge"
    FERRARI = "Ferrari"
    FIAT = "Fiat"
    FORD = "Ford"
    GENESIS = "Genesis"
    GMC = "GMC"
    HONDA = "Honda"
    HYUNDAI = "Hyundai"
    INFINITI = "Infiniti"
    JAGUAR = "Jaguar"
    JEEP = "Jeep"
    KIA = "Kia"
    LAMBORGHINI = "Lamborghini"
    LAND_ROVER = "Land Rover"
    LINCOLN = "Lincoln"
    LOTUS = "Lotus"
    MASERATI = "Maserati"
    MAZDA = "Mazda"
    MCLAREN = "McLaren"
    MERCEDES = "Mercedes-Benz"
    MINI = "Mini"
    MITSUBISHI = "Mitsubishi"
    NISSAN = "Nissan"
    OPEL = "Opel"
    PAGANI = "Pagani"
    PEUGEOT = "Peugeot"
    PORSCHE = "Porsche"
    RAM = "Ram"
    RENAULT = "Renault"
    ROLLS_ROYCE = "Rolls Royce"
    SKODA = "Skoda"
    SUBARU = "Subaru"
    SUZUKI = "Suzuki"
    TESLA = "Tesla"
    TOYOTA = "Toyota"
    VOLKSWAGEN = "Volkswagen"
    VOLVO = "Volvo"
