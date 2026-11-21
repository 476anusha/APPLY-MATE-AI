from typing import Any, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An unexpected error occurred",
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(AppException):
    def __init__(
        self,
        detail: str = "Could not validate credentials",
        headers: Optional[dict[str, Any]] = None,
    ):
        auth_headers = {"WWW-Authenticate": "Bearer"}
        if headers:
            auth_headers.update(headers)
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=auth_headers,
        )


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationException(AppException):
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class UsageLimitException(AppException):
    def __init__(self, detail: str = "Usage limit exceeded for your subscription plan"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail
        )


# Convenient aliases
NotFoundError = NotFoundException
UnauthorizedError = UnauthorizedException
AuthenticationError = UnauthorizedException
ForbiddenError = ForbiddenException
PermissionDeniedError = ForbiddenException
ConflictError = ConflictException
ValidationError = ValidationException
UsageLimitError = UsageLimitException
