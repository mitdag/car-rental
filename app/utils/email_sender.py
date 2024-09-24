from urllib.parse import urlencode
from typing import Dict


# This function simulates a signup confirmation mail.
# Lint that is to be sent via email is printed on the console
# When the link is clicked it calls confirmation end point and signup process finishes
def send_signup_confirmation_email(
    receiver_address: str, path: str, params: Dict, expires: int
):
    print("Thank you for signing up Car Rental App")
    print("Please click the following link to confirm:")
    print(f"{path}?{urlencode(params)}")
    print(f"(This link expires in {expires} day(s)")
