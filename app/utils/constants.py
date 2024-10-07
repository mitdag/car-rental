# This is the default value if no the limit value is specified for endpoint
QUERY_LIMIT_DEFAULT = 20

# This is the max value for the limit values in endpoints
QUERY_LIMIT_MAX = 100

# Lifespan of signup and forgot password links (sent via email)
CONFIRMATION_EXPIRE_PERIOD_IN_DAYS = 1

# Life span of access token in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Life span of refresh token in days
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Path to the profile pictures in mounted "static" directory (mounted in main.py)
PROFILE_PICTURES_PATH = "images/profile-pictures"

# Default profile picture for user accounts (if no picture is uploaded by the user)
DEFAULT_PROFILE_PICTURE_FILE = "egg_head.png"

# Path to the car pictures in mounted "static" directory (mounted in main.py)
CAR_IMAGES_PATH = "images/car-images"

# A car ce be reserved up to this weeks starting form today.
LATEST_START_DATE_OF_RENTAL_IN_WEEKS = 6 * 4

# Maximum rental period in weeks a car can be rented.
MAX_RENTAL_PERIOD_IN_WEEKS = 8
