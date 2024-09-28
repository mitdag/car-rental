"""
Car Router

This module provides endpoints for managing car entries in the database.
It allows users to create, read, update, and delete car records.
Some actions require user authentication.
"""

from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core.database import get_db
from app.schemas.car import CarBase, CarDisplay
from app.schemas import constants
from app.schemas.enums import (
    CarSearchSortType,
    CarSearchSortDirection,
    CarEngineType,
    CarTransmissionType,
)
from app.services import car

router = APIRouter(prefix="/car", tags=["car"])


@router.post(
    "/",
    response_model=CarDisplay,
    summary="Create a car",
    description="Create a new car entry. Requires authenticated user.",
)
def create_car(
    request: CarBase,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """
    Create a new car entry in the database.

    Args:
        request (CarBase): The details of the car to create.
        db (Session): Database session dependency.
        current_user (Any): The authenticated user creating the car.

    Returns:
        CarDisplay: The newly created car.
    """
    return car.create_car(db, request)


@router.get(
    "/",
    response_model=List[CarBase],
    summary="Get all cars",
    description="Retrieve a list of all cars from the database.",
)
def read_cars(db: Session = Depends(get_db)) -> List[CarBase]:
    """
    Retrieve all car entries from the database.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[CarBase]: A list of all cars in the database.
    """
    return car.get_cars(db)


@router.get(
    path="/search",
    summary="Search cars",
    description="Filter car search based on distance, city, booking periods, engine type"
    " transmission type, price and make. Sort result accordingly.",
)
def search_car(
    distance_km: float = Query(
        default=None,
        description="Radius of the search in kilometers "
        "(ignored if search_in_city is also set)",
    ),
    search_in_city: str = Query(default=None, description="Name of the city to search"),
    renter_lat: float = Query(None, description="Latitude of the user's location"),
    renter_lon: float = Query(None, description="Longitude of the user's location"),
    booking_date_start: datetime = Query(
        None, description="Start day of the booking. (NOT IMPLEMENTED YET)"
    ),
    booking_date_end: datetime = Query(
        None, description="End day of the booking. (NOT IMPLEMENTED YET)"
    ),
    engine_type: str = Query(
        None, description=f"Any of the types {CarEngineType.list()}"
    ),
    transmission_type: str = Query(
        None, description=f"Any of the types {CarTransmissionType.list()}"
    ),
    price_min: int = Query(None, description="Minimum daily price for the rent"),
    price_max: int = Query(None, description="Maximum daily price for the rent"),
    make: str = Query(None, description="Make of the car"),
    sort: CarSearchSortType = Query(None, description="Sort parameter"),
    sort_direction: CarSearchSortDirection = Query(None, description="Sort direction"),
    skip: int = Query(default=0, description="Used for pagination for the requests."),
    limit: int = Query(
        constants.QUERY_LIMIT_DEFAULT,
        description=f"Length of the response list (max: {constants.QUERY_LIMIT_MAX})",
    ),
    db: Session = Depends(get_db),
):
    return car.search_cars(
        distance_km=distance_km,
        renter_lat=renter_lat,
        renter_lon=renter_lon,
        booking_date_start=booking_date_start,
        booking_date_end=booking_date_end,
        search_in_city=search_in_city,
        engine_type=engine_type,
        transmission_type=transmission_type,
        price_min=price_min,
        price_max=price_max,
        make=make,
        sort=sort,
        sort_direction=sort_direction,
        skip=skip,
        limit=min(limit, constants.QUERY_LIMIT_MAX),
        db=db,
    )


@router.get(
    "/{car_id}",
    response_model=CarDisplay,
    summary="Get car by ID",
    description="Retrieve details of a car by its ID.",
)
def read_car(car_id: int, db: Session = Depends(get_db)) -> CarDisplay:
    """
    Retrieve a car entry from the database by its ID.

    Args:
        car_id (int): The ID of the car to retrieve.
        db (Session): Database session dependency.

    Returns:
        CarDisplay: The details of the car with the specified ID.
    """
    return car.get_car(db, car_id)


@router.put(
    "/{car_id}",
    summary="Update car details",
    description="Update the details of a car by its ID. Requires authentication.",
)
def update_car(
    car_id: int,
    request: CarBase,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """
    Update a car entry in the database by its ID.

    Args:
        car_id (int): The ID of the car to update.
        request (CarBase): The updated car data.
        db (Session): Database session dependency.
        current_user (Any): The authenticated user performing the update.

    Returns:
        Any: The updated car data after the operation.
    """
    return car.update_car(db, car_id, request)


@router.delete(
    "/{car_id}",
    summary="Delete a car",
    description="Delete a car from the database by its ID. Requires authentication.",
)
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """
    Delete a car entry from the database by its ID.

    Args:
        car_id (int): The ID of the car to delete.
        db (Session): Database session dependency.
        current_user (Any): The authenticated user performing the deletion.

    Returns:
        Any: The result of the delete operation.
    """
    return car.delete_car(db, car_id)
