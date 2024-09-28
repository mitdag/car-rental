import os
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import insert
from fastapi import Depends
from fastapi import APIRouter
from random import randint, random
from datetime import datetime

from app.core import database
from app.models.address import DBAddress
from app.models.car import DBCar
from app.models.user import DBUser
from app.schemas.enums import LoginMethod, UserType
from app.utils.hash import Hash

email_providers = ["google.com", "hotmail.com", "yahoo.com"]
login_methods = [
    LoginMethod.EMAIL,
    LoginMethod.GOOGLE,
    LoginMethod.APPLE,
    LoginMethod.FACEBOOK,
]

router = APIRouter(prefix="/test", tags=["test"])


def read_file(file_name):
    buf = []
    current_dir = Path(os.path.dirname(__file__)).as_posix()
    with open(f"{current_dir}/txt_files/{file_name}", "r") as in_file:
        for line in in_file:
            buf.append(line.strip())
    return buf


# @router.get("/create-test-all")
def create_test_all(db: Session = Depends(database.get_db)):
    create_test_users(db)
    create_test_cars(db)
    create_test_addresses(db)


# @router.get("/create-test-users")
def create_test_users(db: Session = Depends(database.get_db)):
    current_dir = Path(os.path.dirname(__file__)).as_posix()
    users = []
    with open(f"{current_dir}/txt_files/names.txt", "r") as names_file:
        with open(f"{current_dir}/txt_files/last_names.txt", "r") as last_names_file:
            line_no = 0
            for name in names_file:
                last_name = last_names_file.readline().strip()
                users.append(
                    {
                        "name": name,
                        "last_name": last_name,
                        "email": f"{name}.{last_name}_{randint(1700, 1000000)}@{email_providers[randint(0, 2)]}",
                        "password": Hash.bcrypt("12345"),
                        "login_method": login_methods[randint(0, 3)],
                        "phone_number": f"+31{''.join([str(randint(0, 9)) for i in range(0, 10)])}",
                        "user_type": UserType.USER,
                        "is_verified": True,
                        "created_at": datetime.utcnow(),
                        "last_login": datetime.utcnow(),
                    }
                )
                line_no += 1
                if line_no % 100 == 0:
                    db.execute(insert(DBUser), users)
                    db.commit()
                    users.clear()

    if len(users) > 0:
        db.execute(insert(DBUser), users)
        db.commit()
    return "create_test_users done"


# @router.get("/create-test-addresses")
def create_test_addresses(db: Session = Depends(database.get_db)):
    states = ["DR", "FL", "FR", "GE", "GR", "LI", "NB", "NH", "OV", "ZH", "UT", "ZE"]

    streets = read_file("streets.txt")
    cities = read_file("cities.txt")

    addresses = []
    for i in range(1, 5001):
        addresses.append(
            {
                "user_id": i,
                "street": streets[randint(0, len(streets) - 1)],
                "number": randint(1, 500),
                "postal_code": ("2" if randint(0, 1) == 0 else "3")
                + f"{''.join([str(randint(0, 9)) for i in range(1, 4)])}"
                + f"{str(chr(randint(ord('A'), ord('Z'))))}{str(chr(randint(ord('A'), ord('Z'))))}",
                "city": cities[randint(0, len(cities) - 1)],
                "state": states[randint(0, len(states) - 1)],
                "country": "Netherlands",
                "latitude": 50 + randint(0, 3) + random(),
                "longitude": 4 + randint(0, 2) + random(),
                "created_at": datetime.utcnow(),
                # w-s: 50.71159817163813, 4.122884687333848
                # e-n: 53.4254164285873, 6.836507489963032
            }
        )
        if len(addresses) == 100:
            db.execute(insert(DBAddress), addresses)
            db.commit()
            addresses.clear()

    if len(addresses) > 0:
        db.execute(insert(DBAddress), addresses)
        db.commit()
        addresses.clear()

    return "create_test_addresses done"


# @router.get("/create-cars")
def create_test_cars(db: Session = Depends(database.get_db)):
    cars = []
    makes = read_file("car_make.txt")
    models = read_file("car_model.txt")
    car_owners = [randint(1, 5000) for _ in range(1, 700)]

    for i in range(0, len(car_owners)):
        rand_index = randint(0, len(makes) - 1)
        cars.append(
            {
                "owner_id": car_owners[i],
                "make": makes[rand_index],
                "model": models[rand_index],
                "year": randint(2015, 2024),
                "transmission_type": "manual" if randint(0, 1) == 0 else "automatic",
                "motor_type": "Gasoline" if randint(0, 1) == 0 else "Electric",
                "price_per_day": randint(75, 150),
                "description": "",
                "is_listed": True,
            }
        )
        if len(cars) == 100:
            db.execute(insert(DBCar), cars)
            db.commit()
            cars.clear()
    if len(cars) > 0:
        db.execute(insert(DBCar), cars)
        db.commit()
        cars.clear()

    return "create_test_cars"
