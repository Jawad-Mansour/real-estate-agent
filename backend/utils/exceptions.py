"""
Custom exceptions for the application
Provides structured error handling for FastAPI
"""

from typing import Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class AppException(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, status_code: int = 400, details: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


class NotFoundException(AppException):
    """Raised when a resource is not found"""
    def __init__(self, message: str, resource_type: str = None):
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class ModelLoadException(AppException):
    """Raised when model fails to load"""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handler for Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "status": "error",
            "message": "Validation error",
            "errors": errors
        }
    )


async def app_exception_handler(request: Request, exc: AppException):
    """Handler for custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status": "error",
            "message": exc.message,
            "details": exc.details
        }
    )