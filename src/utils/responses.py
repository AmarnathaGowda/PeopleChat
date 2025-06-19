"""
Standardized API response formats
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime


class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def success_response(
    data: Any = None,
    message: str = "Success",
    **kwargs
) -> Dict[str, Any]:
    """
    Create a success response
    
    Args:
        data: Response data
        message: Success message
        **kwargs: Additional fields
        
    Returns:
        Success response dictionary
    """
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }


def error_response(
    message: str,
    error_code: str = "ERROR",
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 500
) -> Dict[str, Any]:
    """
    Create an error response
    
    Args:
        message: Error message
        error_code: Error code
        details: Additional error details
        status_code: HTTP status code
        
    Returns:
        Error response dictionary
    """
    return {
        "success": False,
        "message": message,
        "error": {
            "code": error_code,
            "details": details or {},
            "status_code": status_code
        },
        "timestamp": datetime.utcnow().isoformat()
    }


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "Success"
) -> Dict[str, Any]:
    """
    Create a paginated response
    
    Args:
        items: List of items
        total: Total number of items
        page: Current page number
        page_size: Items per page
        message: Success message
        
    Returns:
        Paginated response dictionary
    """
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "success": True,
        "message": message,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }