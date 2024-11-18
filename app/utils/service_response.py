from enum import Enum
from typing import Any
from fastapi import status, HTTPException


class ServiceResponseStatus(int, Enum):
    SUCCESS = status.HTTP_200_OK,
    BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    UNAUTHORISED = status.HTTP_401_UNAUTHORIZED
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    FORBIDDEN = status.HTTP_403_FORBIDDEN
    UNPROCESSABLE_ENTITY = status.HTTP_422_UNPROCESSABLE_ENTITY
    INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR


class ServiceResponse:
    def __init__(self, status: ServiceResponseStatus, message: str, data: Any):
        self.status = status
        self.message = message
        self.data = data

    def create_http_exception(self):
        return HTTPException(
            status_code=self.status,
            detail=self.message
        )
