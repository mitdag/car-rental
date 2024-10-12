import os
from datetime import datetime, timedelta
from pathlib import Path
from random import choice, randint, random
from time import time

from fastapi import APIRouter, Depends, HTTPException, status, Query
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
from app.services import car as car_service

email_providers = ["google.com", "hotmail.com", "yahoo.com"]

router = APIRouter(prefix="/test", tags=["test"])

DB_WRITE_COUNT = 500


def read_file(file_name):
    buf = []
    current_dir = Path(os.path.dirname(__file__)).as_posix()
    with open(f"{current_dir}/txt_files/{file_name}", "r") as in_file:
        for line in in_file:
            buf.append(line.strip())
    return buf


@router.get("/create-test-all")
def create_test_all(
    number_of_users: int = Query(
        default=1000,
        lt=5001,
        gt=19,
        description="Number of all users (including the car owners)",
    ),
    number_of_owners: int = Query(
        default=400, lt=701, gt=9, description="An owner may have multiple cars."
    ),
    number_of_cars: int = Query(default=500, lt=701, gt=9),
    max_rent_count_per_car: int = Query(default=50, lt=101, gt=9),
    min_rent_count_per_car: int = Query(default=10, lt=31, gt=4),
    db: Session = Depends(database.get_db),
):
    if number_of_cars < number_of_owners:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of cars must be equal or greater than the owners",
        )
    print("")
    start_time = time()
    create_test_users(number_of_users, db)
    print(f"{number_of_users} users created in {time() - start_time:.2} sec.")

    start_time = time()
    create_test_cars(number_of_cars, number_of_owners, number_of_users, db)
    print(f"{number_of_cars} cars created in {time() - start_time:.2} sec.")

    start_time = time()
    create_test_addresses(number_of_users, db)
    print(f"{number_of_users} addresses created in {time() - start_time:.2} sec.")

    start_time = time()
    rent_cnt, rev_cnt = create_rentals_and_reviews(
        number_of_users, max_rent_count_per_car, min_rent_count_per_car, db
    )
    print(
        f"{rent_cnt} rentals and {rev_cnt} "
        f"reviews created in {time() - start_time:.2f} sec."
    )
    print("All done")
    return {
        "users_created": number_of_users,
        "addresses_created": number_of_users,
        "cars_created": number_of_cars,
        "owners_created": number_of_owners,
        "rentals_created": rent_cnt,
        "reviews_created": rev_cnt,
    }


# @router.get("/create-test-users")
def create_test_users(number_of_users: int, db: Session = Depends(database.get_db)):
    try:
        db.query(DBUser).delete()
        db.commit()
        # print("Users table is cleared")
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
            for name_in_file in names_file:
                name = name_in_file.strip()
                last_name = last_names_file.readline().strip()
                users.append(
                    {
                        "name": name,
                        "last_name": last_name,
                        "email": f"{name}.{last_name}_"
                        f"{randint(1700, 1000000)}"
                        f"@{email_providers[randint(0, 2)]}",
                        # Hash.bcrypt("12345")
                        "password": "$2b$12$nOhIiL3KHgVhst2Y5YZjQ."
                        "CBUn6gsSrdre3ljlEjoD4FgjY9Uq/bu",
                        "login_method": choice(list(LoginMethod)),
                        "phone_number": f"+31"
                        f"{''.join([str(randint(0, 9)) for _ in range(0, 10)])}",
                        "user_type": UserType.USER,
                        "is_verified": True,
                        "created_at": datetime.utcnow(),
                        "last_login": datetime.utcnow(),
                    }
                )
                line_no += 1
                if line_no == DB_WRITE_COUNT:
                    db.execute(insert(DBUser), users)
                    db.commit()
                    users.clear()
                if line_no == number_of_users:
                    break
    if len(users) > 0:
        db.execute(insert(DBUser), users)
        db.commit()
    return "create_test_users done"


# @router.get("/create-test-addresses")
def create_test_addresses(number_of_users: int, db: Session = Depends(database.get_db)):
    try:
        db.query(DBAddress).delete()
        db.commit()
        # print("Addresses table is cleared")
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
    for i in range(1, number_of_users + 1):
        addresses.append(
            {
                "user_id": i,
                "street": streets[randint(0, len(streets) - 1)],
                "number": randint(1, 500),
                "postal_code": f"{'2' if randint(0, 1) == 0 else '3'}"
                f"{''.join([str(randint(0, 9)) for _ in range(1, 4)])}"
                f"{str(chr(randint(ord('A'), ord('Z'))))}"
                f"{str(chr(randint(ord('A'), ord('Z'))))}",
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
        if len(addresses) == DB_WRITE_COUNT:
            db.execute(insert(DBAddress), addresses)
            db.commit()
            addresses.clear()

    if len(addresses) > 0:
        db.execute(insert(DBAddress), addresses)
        db.commit()
        addresses.clear()

    return "create_test_addresses done"


def create_test_cars_for_owners(
    car_owners: [int], db: Session = Depends(database.get_db)
):
    cars = []
    makes = read_file("car_make.txt")
    models = read_file("car_model.txt")
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
        if len(cars) == DB_WRITE_COUNT:
            db.execute(insert(DBCar), cars)
            db.commit()
            cars.clear()
    if len(cars) > 0:
        db.execute(insert(DBCar), cars)
        db.commit()
        cars.clear()


# @router.get("/create-cars")
def create_test_cars(
    number_of_cars: int,
    number_of_owners: int,
    number_of_users: int,
    db: Session = Depends(database.get_db),
):
    try:
        db.query(DBCar).delete()
        db.commit()
        # print("Cars table is cleared")
    except Exception as exc:
        db.rollback()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete entries in cars table ({exc}) ",
        )

    car_owners = set()
    while len(car_owners) < number_of_owners:
        car_owners.add(randint(1, number_of_users))

    create_test_cars_for_owners(list(car_owners), db)

    remaining_car_owners = set()
    while len(remaining_car_owners) < number_of_cars - number_of_owners:
        remaining_car_owners.add(choice(list(car_owners)))

    create_test_cars_for_owners(list(remaining_car_owners), db)
    return "create_test_cars"


# @router.get("/test-create-rentals")
def create_rentals_and_reviews(
    number_of_users: int,
    max_rent_count_per_car: int,
    min_rent_count_per_car: int,
    db=Depends(database.get_db),
):
    try:
        db.query(DBRental).delete()
        db.commit()
        # print("Rentals table is cleared")
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
        # print("Reviews table is cleared")
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
    rent_cnt = 0
    rev_cnt = 0
    for user, car in owners_and_cars:
        start_date: datetime = datetime.now() + timedelta(days=30)
        number_of_rentals = randint(min_rent_count_per_car, max_rent_count_per_car + 1)
        for _ in range(1, number_of_rentals):
            renter = randint(1, number_of_users + 1)
            while renter == user:
                renter = randint(1, number_of_users + 1)
            car_in_db: DBCar = car_service.get_car(db, car)
            start_d = start_date + timedelta(days=randint(1, 3))
            end_d = start_d + timedelta(days=randint(1, 5))
            rental = {
                # we give id manually because we use it also with the review
                "id": rental_id,
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
                rental["status"] = RentalStatus.RESERVED.name
            elif now < rental["start_date"]:
                rental["status"] = RentalStatus.RESERVED.name
            rentals.append(rental)

            start_date = start_d - timedelta(days=randint(3, 10))

            if randint(1, 5) in [1, 2, 3]:
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

            if len(rentals) == DB_WRITE_COUNT:
                db.execute(insert(DBRental), rentals)
                db.commit()
                rent_cnt += len(rentals)
                rentals.clear()
            if len(reviews) == DB_WRITE_COUNT:
                db.execute(insert(DBReview), reviews)
                db.commit()
                rev_cnt += len(reviews)
                reviews.clear()

    if len(rentals) > 0:
        db.execute(insert(DBRental), rentals)
        db.commit()
        rent_cnt += len(rentals)
    if len(reviews) > 0:
        db.execute(insert(DBReview), reviews)
        db.commit()
        rev_cnt += len(reviews)

    return rent_cnt, rev_cnt
