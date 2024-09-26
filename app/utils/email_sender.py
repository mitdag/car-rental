from urllib.parse import urlencode
from typing import Dict


# This function simulates a signup confirmation mail.
# Lint that is to be sent via email is printed on the console
# When the link is clicked it calls confirmation end point and signup process finishes
def send_signup_confirmation_email(
    receiver_address: str, path: str, params: Dict, expires: int
):
    line_length = 120
    url = f"{path}?{urlencode(params)}"
    exp = f"(This link expires in {expires} day(s))"
    print("\n\n")
    print(f"{(str('')):*>{line_length}}")
    print(f"**{(str('C O N F I R M T I O N     M A I L')): ^{line_length - 4}}**")
    print(f"{(str('')):*>{line_length}}")
    print(f"**{(str('**')): >{line_length - 2}}")
    print(f"**{(str('Thank you for signing up Car Rental App')): ^{line_length - 4}}**")
    print(
        f"**{(str('Please click the following link to confirm your signup:')): ^{line_length - 4}}**"
    )
    print(f"**{(str('**')): >{line_length - 2}}")
    print(f"**{url: ^{line_length - 4}}**")
    print(f"**{(str('**')): >{line_length - 2}}")
    print(f"**{exp: ^{line_length - 4}}**")
    print(f"{(str('')):*>{line_length}}")
    print("\n\n")
