"""
Custom exception classes
"""
from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """Base exception class for API errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(BaseAPIException):
    """Authentication failed"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTH_FAILED")


class AuthorizationError(BaseAPIException):
    """Authorization failed"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")


class NotFoundError(BaseAPIException):
    """Resource not found"""
    
    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier {identifier} not found"
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ValidationError(BaseAPIException):
    """Validation error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR", details=details)


class ExternalAPIError(BaseAPIException):
    """External API call failed"""
    
    def __init__(self, service: str, message: str):
        full_message = f"External service '{service}' error: {message}"
        super().__init__(full_message, status_code=502, error_code="EXTERNAL_API_ERROR")


class RateLimitError(BaseAPIException):
    """Rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_EXCEEDED")