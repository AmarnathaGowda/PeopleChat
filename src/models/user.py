"""
User-related database models
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer
from sqlalchemy.sql import func
from datetime import datetime
import enum

from models.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr"
    ADMIN = "admin"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    department = Column(String(100))
    manager_id = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships will be added as we create other models
    
    def __repr__(self):
        return f"<User(employee_id={self.employee_id}, email={self.email})>"