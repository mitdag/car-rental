"""
Car Router

This module provides endpoints for managing car entries in the database.
It allows users to create, read, update, and delete car records.
Some actions require user authentication.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core.database import get_db
from app.schemas.car import CarBase, CarDisplay
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
