from enum import Enum


class ErrorCode(str, Enum):
    CAR_NOT_FOUND = "car_not_found"
    CAR_NOT_AVAILABLE = "car_not_available"
    ACTIVE_RENTAL_EXISTS = "active_rental_exists"
    RENTAL_NOT_FOUND = "rental_not_found"
    RENTAL_ALREADY_ENDED = "rental_already_ended"


class BusinessError(Exception):
    error_code: ErrorCode

    def __init__(self, message: str | None = None):
        # default message = enum value
        super().__init__(message or self.error_code.value)


class CarNotFound(BusinessError):
    error_code = ErrorCode.CAR_NOT_FOUND


class CarNotAvailable(BusinessError):
    error_code = ErrorCode.CAR_NOT_AVAILABLE


class ActiveRentalExists(BusinessError):
    error_code = ErrorCode.ACTIVE_RENTAL_EXISTS


class RentalNotFound(BusinessError):
    error_code = ErrorCode.RENTAL_NOT_FOUND


class RentalAlreadyEnded(BusinessError):
    error_code = ErrorCode.RENTAL_ALREADY_ENDED
