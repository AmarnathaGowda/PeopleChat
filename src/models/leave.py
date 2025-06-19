"""
Leave management related models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Date, Enum, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from models.database import Base


class LeaveType(str, enum.Enum):
    """Leave type enumeration"""
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    COMP_OFF = "comp_off"
    LOP = "loss_of_pay"


class LeaveStatus(str, enum.Enum):
    """Leave request status"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveRequest(Base):
    """Leave request model"""
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type = Column(Enum(LeaveType), nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    number_of_days = Column(Float, nullable=False)
    
    reason = Column(Text, nullable=False)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.DRAFT)
    
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_comments = Column(Text, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # External system reference
    external_ref_id = Column(String(100), nullable=True)
    
    # Relationships
    employee = relationship("User", foreign_keys=[employee_id], backref="leave_requests")
    approver = relationship("User", foreign_keys=[approver_id], backref="approved_leaves")


class LeaveBalance(Base):
    """Employee leave balance model"""
    __tablename__ = "leave_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    leave_type = Column(Enum(LeaveType), nullable=False)
    year = Column(Integer, nullable=False)
    
    total_allocated = Column(Float, default=0)
    used = Column(Float, default=0)
    pending = Column(Float, default=0)
    available = Column(Float, default=0)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    employee = relationship("User", backref="leave_balances")
    
    # Composite unique constraint
    __table_args__ = (
        {"schema": "dbo", "extend_existing": True},
    )