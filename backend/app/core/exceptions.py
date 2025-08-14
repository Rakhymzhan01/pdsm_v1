from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import traceback
from typing import Union
from app.core.logging import logger

class PDMSException(Exception):
    """Base exception class for PDMS application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseError(PDMSException):
    """Database related errors"""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status_code=500)

class AuthenticationError(PDMSException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(PDMSException):
    """Authorization related errors"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403)

class ValidationError(PDMSException):
    """Validation related errors"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)

class NotFoundError(PDMSException):
    """Resource not found errors"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

# Global exception handlers
async def pdms_exception_handler(request: Request, exc: PDMSException):
    """Handle custom PDMS exceptions"""
    logger.error(f"PDMS Exception: {exc.message} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP Exception: {exc.detail} | Status: {exc.status_code} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation Error: {exc.errors()} | Path: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "status_code": 422,
            "path": str(request.url.path)
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors"""
    logger.error(f"Database Error: {str(exc)} | Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database operation failed",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled Exception: {str(exc)} | Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )