"""
Car Router

This module provides endpoints for managing car entries in the database.
It allows users to create, read, update, and delete car records.
Some actions require user authentication.
"""

from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Path,
    Query,
    UploadFile,
    status,
)
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.auth import oauth2
from app.core.database import get_db
from app.schemas.car import CarCreate, CarDisplay, CarUpdate
from app.schemas.enums import (
    CarEngineType,
    CarMake,
    CarSearchSortType,
    CarTransmissionType,
    SortDirection,
    UserType,
)
from app.schemas.rental import RentalPeriod
from app.services import car
from app.utils import constants

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post(
    "/",
    response_model=CarDisplay,
    summary="Create a car",
    description="Create a new car entry. Requires authenticated user.",
    status_code=status.HTTP_201_CREATED,
)
def create_car(
    request: CarCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.complete_user_profile_only),
):
    """
    Create a new car entry in the database.

    Args:
        request (CarCreate): The details of the car to create.
        db (Session): Database session dependency.
        current_user (Any): The authenticated user creating the car.

    Returns:
        CarDisplay: The newly created car.

    Raises:
        HTTPException: If car creation fails.
    """

    new_car = car.create_car(db, request, current_user.id)

    return new_car


# Pagination example
# @router.get(
#     "/",
#     response_model=Page[CarDisplay],
#     summary="List all cars",
#     description="Retrieve a paginated list of all cars from the database.",
# )
# def list_cars(db: Session = Depends(get_db)) -> Page[CarDisplay]:
#     """
#     Retrieve all car entries from the database with pagination options.

#     Args:
#         db (Session): Database session dependency.
#         skip (int): Number of records to skip (used for pagination).
#         limit (int): Maximum number of records to return (used for pagination).

#     Returns:
#         List[CarBase]: A list of cars in the database based on pagination.
#     """
#     return paginate(car.get_cars(db))


@router.get(
    path="/",
    summary="Search and list cars",
    description="Search and retrieve a paginated list of cars based on various filters. Filter car search based on distance, city, booking periods, engine type"
    " transmission type, price and make. Sort result accordingly.",
)
def search_car(
    distance_km: float = Query(
        default=None,
        ge=1,
        description="Radius of the search in kilometers "
        "(ignored if search_in_city is also set)",
    ),
    search_in_city: str = Query(default=None, description="Name of the city to search"),
    renter_lat: float = Query(
        None, ge=-90, le=90, description="Latitude of the user's location"
    ),
    renter_lon: float = Query(
        None, ge=-180, le=180, description="Longitude of the user's location"
    ),
    availability_period: RentalPeriod = Depends(),
    engine_type: CarEngineType = Query(None, description="Select an engine type"),
    transmission_type: CarTransmissionType = Query(
        None, description="Select a transmission type"
    ),
    price_min: int = Query(None, ge=0, description="Minimum daily price for the rent"),
    price_max: int = Query(None, ge=1, description="Maximum daily price for the rent"),
    make: str = Query(None, description="Make of the car"),
    sort: CarSearchSortType = Query(None, description="Sort parameter"),
    sort_direction: SortDirection = Query(None, description="Sort direction"),
    skip: int = Query(
        default=0, ge=0, description="Used for pagination for the requests."
    ),
    limit: int = Query(
        constants.QUERY_LIMIT_DEFAULT,
        ge=1,
        le=constants.QUERY_LIMIT_MAX,
        description="Length of the response list",
    ),
    db: Session = Depends(get_db),
):
    return car.search_cars(
        distance_km=distance_km,
        renter_lat=renter_lat,
        renter_lon=renter_lon,
        availability_period=availability_period,
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


# @router.get("/test")
# def test(db=Depends(get_db)):
#     return test_rating(db)


@router.get(
    "/{car_id}",
    response_model=CarDisplay,
    summary="Get car by ID",
    description="Retrieve details of a car by its ID.",
)
def get_car(
    car_id: int = Path(..., ge=1, description="The ID of the car to retrieve"),
    db: Session = Depends(get_db),
) -> CarDisplay:
    """
    Retrieve a car entry from the database by its ID.

    Args:
        car_id (int): The ID of the car to retrieve.
        db (Session): Database session dependency.

    Returns:
        CarDisplay: The details of the car with the specified ID.
    """
    try:
        db_car = car.get_car(db, car_id)
        # Check if the database car record has different model than response model
        CarDisplay.model_validate(db_car)
        return db_car
    except ValidationError as e:
        # Validation Error for pydantic
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error occurred: {e.errors()}",
        )

    except Exception as e:
        # Catch any other unforeseen errors.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.put(
    "/{car_id}",
    summary="Update car details",
    description="Update the details of a car by its ID. Requires authentication.",
)
def update_car(
    car_id: int,
    request: CarUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """
    Update a car entry in the database by its ID.

    Args:
        car_id (int): The ID of the car to update.
        request (CarUpdate): The updated car data.
        db (Session): Database session dependency.
        current_user (Any): The authenticated user performing the update.

    Returns:
        Any: The updated car data after the operation.
    """
    db_car = car.get_car(db, car_id)

    if current_user.user_type != UserType.ADMIN and db_car.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this car",
        )

    return car.update_car(db, car_id, request)


@router.delete(
    "/{car_id}",
    summary="Delete a car",
    description="Delete a car from the database by its ID. Requires authentication.",
    tags=["cars"],  # admin deleted
    status_code=status.HTTP_204_NO_CONTENT,
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
    db_car = car.get_car(db, car_id)

    if current_user.user_type != UserType.ADMIN and db_car.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this car",
        )

    return car.delete_car(db, car_id)


@router.post(
    "/{car_id}/car-pictures",
    status_code=status.HTTP_201_CREATED,
)
def upload_car_picture(
    car_id: int = Path(...),
    picture: UploadFile = File(
        ...,
        description="Upload an image (JPEG, PNG, BMP, WEBP)",
        openapi_extra={"examples": {"image": {"content": {"image/*": {}}}}},
    ),
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """
    Uploads a picture for a specified car.

    This endpoint allows users to upload an image associated with a car identified by
    its ID. Only users with admin privileges or the car owner can upload a picture.

    Args:
        car_id (int): The ID of the car for which the picture is being uploaded.
        picture (UploadFile): The image file to be uploaded. Supported formats include
                              JPEG, PNG, BMP, and WEBP.
        db (Session): Database session dependency.
        current_user: The user attempting to upload the picture. Retrieved from the
                      authentication system.

    Raises:
        HTTPException:
            - 400: If no picture is provided.
            - 403: If the user is not authorized to upload a picture for the specified car.

    Returns:
        Response: The response from the car picture upload process.
    """
    if not picture:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Provide a picture"
        )

    db_car = car.get_car(db, car_id)

    if current_user.user_type != UserType.ADMIN and db_car.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this car",
        )

    return car.upload_car_picture(picture, db_car.id)


@router.get("/{car_id}/car-pictures", response_model=List[str])
def get_car_pictures(
    car_id: int = Path(...),
    db: Session = Depends(get_db),
):
    """
    Get a list of all picture filenames for a specific car.

    Args:
        car_id (int): The ID of the car.
        db (Session): Database session dependency.
    Returns:
        List[str]: A list of filenames of pictures associated with the car.
    """

    # Raise error if car doesnt exist
    car.get_car(db, car_id)

    pictures_list = car.get_car_pictures(car_id)
    pictures_list = [
        f"/static/images/car-images/car_{car_id:06}/" + picture
        for picture in pictures_list
    ]
    return pictures_list


@router.delete(
    "/{car_id}/car-pictures/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_car_picture(
    car_id: int = Path(...),
    filename: str = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """
    Delete a specific picture for a car.

    Args:
        car_id (int): The ID of the car.
        filename (str): The name of the file to delete.
        db (Session): Database session dependency.
        current_user: The authenticated user.

    Returns:
        dict: A message indicating whether the deletion was successful.
    """
    db_car = car.get_car(db, car_id)

    if current_user.user_type != UserType.ADMIN and db_car.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this car's pictures",
        )

    success = car.delete_car_picture(car_id, filename)
    if success:
        return {"message": f"Picture {filename} deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Picture {filename} not found for car_id {car_id}",
        )


@router.delete(
    "/{car_id}/car-pictures",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_all_car_pictures(
    car_id: int = Path(...),
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """
    Delete all pictures associated with a specific car.

    Args:
        car_id (int): The ID of the car.
        db (Session): Database session dependency.
        current_user: The authenticated user.

    Returns:
        dict: A message indicating that all pictures were deleted.
    """
    db_car = car.get_car(db, car_id)

    if current_user.user_type != UserType.ADMIN and db_car.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this car's pictures",
        )

    car.delete_all_car_pictures(car_id)
    return {"message": f"All pictures for car_id {car_id} deleted successfully"}


@router.get("/car-makes/", response_model=list)
def get_car_makes():
    """
    Retrieve a list of available car makes.

    This endpoint returns a list of car makes defined in the CarMake enum.
    Each car make is represented as a string value corresponding to its name.

    Responses:
        - 200 OK: A list of car makes available in the system.

    Example Response:
        [
            "Acura",
            "Alfa Romeo",
            "Aston Martin",
            "Audi",
            "Bentley",
            ...
        ]
    """
    return [make.value for make in CarMake]
