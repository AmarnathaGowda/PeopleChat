"""
Authentication service
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from schemas.auth import LoginRequest, TokenResponse, UserResponse
from utils.security import verify_password, create_access_token, hash_password
from utils.logger import get_logger
from config.config import settings

logger = get_logger(__name__)


class AuthService:
    """Authentication service for handling user authentication"""
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning(f"Login attempt for non-existent user: {email}")
            return None
            
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            return None
            
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {email}")
            return None
            
        return user
    
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> Tuple[TokenResponse, User]:
        """
        Process user login
        
        Args:
            db: Database session
            login_data: Login credentials
            
        Returns:
            Tuple of (TokenResponse, User)
            
        Raises:
            HTTPException: If authentication fails
        """
        # Authenticate user
        user = AuthService.authenticate_user(
            db, 
            login_data.email, 
            login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=7)
        
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "type": "access"
            },
            expires_delta=access_token_expires
        )
        
        refresh_token = create_access_token(
            data={
                "sub": str(user.id),
                "type": "refresh"
            },
            expires_delta=refresh_token_expires
        )
        
        logger.info(f"User {user.email} logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_token=refresh_token
        ), user
    
    @staticmethod
    def refresh_token(db: Session, user_id: int) -> TokenResponse:
        """
        Generate new access token using refresh token
        
        Args:
            db: Database session
            user_id: User ID from refresh token
            
        Returns:
            New TokenResponse
            
        Raises:
            HTTPException: If user not found or inactive
        """
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "type": "access"
            },
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token refreshed for user {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    @staticmethod
    def change_password(
        db: Session, 
        user: User, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            db: Database session
            user: User object
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
            
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash and update new password
        user.hashed_password = hash_password(new_password)
        db.commit()
        
        logger.info(f"Password changed for user {user.email}")
        
        return True