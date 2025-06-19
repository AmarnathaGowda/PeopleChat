"""
Authentication API endpoints
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import get_db
from models.user import User
from schemas.auth import (
    LoginRequest, 
    TokenResponse, 
    UserResponse, 
    ChangePasswordRequest,
    RefreshTokenRequest
)
from services.auth_service import AuthService
from api.dependencies import get_current_active_user
from utils.security import decode_access_token
from utils.responses import success_response, error_response
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    User login endpoint
    
    Returns access token and refresh token upon successful authentication.
    """
    try:
        token_response, user = AuthService.login(db, login_data)
        return token_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Refresh access token
    
    Use refresh token to get a new access token.
    """
    try:
        # Decode refresh token
        payload = decode_access_token(refresh_data.refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Generate new access token
        return AuthService.refresh_token(db, int(user_id))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get current user information
    
    Returns the authenticated user's profile information.
    """
    return UserResponse.from_orm(current_user)


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Change user password
    
    Requires current password verification.
    """
    # Validate passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    try:
        AuthService.change_password(
            db,
            current_user,
            password_data.current_password,
            password_data.new_password
        )
        return success_response(message="Password changed successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing password"
        )


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    User logout endpoint
    
    Note: With JWT tokens, logout is typically handled client-side by removing the token.
    This endpoint can be used for audit logging or token blacklisting if implemented.
    """
    logger.info(f"User {current_user.email} logged out")
    return success_response(message="Logged out successfully")