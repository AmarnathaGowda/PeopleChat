"""
Audit logging model
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.database import Base


class AuditLog(Base):
    """Audit log for tracking all system activities"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String(100), nullable=False)  # e.g., "leave_request_created"
    entity_type = Column(String(50), nullable=True)  # e.g., "leave_request"
    entity_id = Column(Integer, nullable=True)
    
    # Store before and after states for changes
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Additional context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    # Changed from 'metadata' to 'audit_metadata'
    audit_metadata = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", backref="audit_logs")