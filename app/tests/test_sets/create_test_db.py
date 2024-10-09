import os
from datetime import datetime, timedelta
from pathlib import Path
from random import choice, randint, random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.core import database
from app.models.address import DBAddress
from app.models.car import DBCar
from app.models.rental import DBRental
from app.models.review import DBReview
from app.models.user import DBUser
from app.schemas.enums import (
    CarEngineType,
    CarTransmissionType,
    LoginMethod,
    UserType,
    RentalStatus,
)
from app.utils.hash import Hash
from app.services import car as car_service

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


@router.get("/create-test-all")
def create_test_all(db: Session = Depends(database.get_db)):
    create_test_users(db)
    create_test_cars(db)
    create_test_addresses(db)
    create_rentals_and_reviews(db)


# @router.get("/create-test-users")
def create_test_users(db: Session = Depends(database.get_db)):
    try:
        db.query(DBUser).delete()
        db.commit()
    except Exception as exc:
        db.rollback()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete entries in users table ({exc}) ",
        )

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
    try:
        db.query(DBAddress).delete()
        db.commit()
    except Exception as exc:
        db.rollback()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete entries in address table ({exc}) ",
        )

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
    try:
        db.query(DBCar).delete()
        db.commit()
    except Exception as exc:
        db.rollback()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete entries in cars table ({exc}) ",
        )
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
                "transmission_type": choice(CarTransmissionType.list()),
                "motor_type": choice(CarEngineType.list()),
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


@router.get("/test-create-rentals")
def create_rentals_and_reviews(db: Session = Depends(database.get_db)):
    try:
        db.query(DBRental).delete()
        db.commit()
    except Exception as exc:
        db.rollback()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete entries in rentals table ({exc}) ",
        )

    try:
        db.query(DBReview).delete()
        db.commit()
    except Exception as exc:
        db.rollback()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete entries in reviews table ({exc}) ",
        )

    owners_and_cars = (
        db.query(DBUser.id, DBCar.id).filter(DBUser.id == DBCar.owner_id).all()
    )

    rental_id = 1

    rentals = []
    reviews = []
    for user, car in owners_and_cars:
        start_date: datetime = datetime.now() - timedelta(days=90)
        for _ in range(1, randint(50, 200)):
            renter = randint(1, 5000)
            while renter == user:
                renter = randint(1, 5000)
            car_in_db: DBCar = car_service.get_car(db, car)
            start_d = start_date + timedelta(days=randint(1, 3))
            end_d = start_d + timedelta(days=randint(1, 5))
            rental = {
                "id": rental_id,  # we give id manually because we use it also with the review
                "car_id": car,
                "renter_id": renter,
                "start_date": start_d,
                "end_date": end_d,
                "total_price": car_in_db.price_per_day * (end_d - start_d).days,
            }
            now = datetime.utcnow()
            if now > rental["end_date"]:
                rental["status"] = RentalStatus.RETURNED.name
            elif rental["start_date"] < datetime.utcnow() < rental["end_date"]:
                rental["status"] = RentalStatus.BOOKED.name
            elif now < rental["start_date"]:
                rental["status"] = RentalStatus.RESERVED.name
            rentals.append(rental)

            start_date = rental["end_date"]

            reviews.append(
                {
                    "rental_id": rental_id,
                    "reviewer_id": renter,
                    "reviewee_id": user,
                    "rating": randint(1, 5),
                    "comment": "",
                    "review_date": rental["end_date"] + timedelta(days=1),
                }
            )

            if randint(1, 4) == 4:
                reviews.append(
                    {
                        "rental_id": rental_id,
                        "reviewer_id": user,
                        "reviewee_id": renter,
                        "rating": randint(1, 5),
                        "comment": "",
                        "review_date": rental["end_date"] + timedelta(days=2),
                    }
                )

            rental_id += 1

            if len(rentals) >= 100:
                db.execute(insert(DBRental), rentals)
                db.commit()
                rentals.clear()
            if len(reviews) >= 100:
                db.execute(insert(DBReview), reviews)
                db.commit()
                reviews.clear()

    if len(rentals) > 0:
        db.execute(insert(DBRental), rentals)
        db.commit()
        rentals.clear()
    if len(reviews) > 0:
        db.execute(insert(DBReview), reviews)
        db.commit()
        reviews.clear()

    return "done"
