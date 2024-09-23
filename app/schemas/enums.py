from enum import Enum


class LoginMethod(Enum):
    EMAIL = 1
    FACEBOOK = 2
    GOOGLE = 3
    APPLE = 4

class UserType(Enum):
    USER = 1,
    ADMIN = 2