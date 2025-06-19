"""
API Key model for external integrations
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.database import Base


class APIKey(Base):
    """API Key model for external integrations"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    
    # Which user created this key
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Permissions/scopes
    scopes = Column(String(500))  # Comma-separated list of scopes
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User", backref="api_keys")