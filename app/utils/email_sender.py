from urllib.parse import urlencode
from typing import Dict


def send_signup_confirmation_email(
        receiver_address: str,
        path: str,
        params: Dict,
        expires: int
):
    print("Thank you for signing up Car Rental App")
    print("Please click the following link to confirm:")
    print(f"{path}?{urlencode(params)}")
    print(f"(This link expires in {expires} day(s)")

    # 'http://127.0.0.1:8000/signup/confirm?id=1&key=111'
    #  http://127.0.0.1:8000/signup/comfirm?key=39677f4e-0b30-41ea-9340-e3098b2861d1&id=6