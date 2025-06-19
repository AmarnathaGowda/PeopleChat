"""
Tax declaration related models
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from models.database import Base


class TaxDeclaration(Base):
    """Tax declaration model"""
    __tablename__ = "tax_declarations"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    financial_year = Column(String(10), nullable=False)  # e.g., "2023-24"
    
    # Salary components
    basic_salary = Column(Float, nullable=False)
    hra = Column(Float, default=0)
    special_allowance = Column(Float, default=0)
    other_allowances = Column(Float, default=0)
    
    # Deductions under different sections
    section_80c = Column(JSON, default={})  # PPF, ELSS, etc.
    section_80d = Column(JSON, default={})  # Medical insurance
    section_80g = Column(JSON, default={})  # Donations
    other_deductions = Column(JSON, default={})
    
    # HRA details
    hra_claimed = Column(Float, default=0)
    rent_paid = Column(Float, default=0)
    metro_city = Column(Boolean, default=False)
    
    # Tax regime selection
    tax_regime = Column(String(20), default="new")  # "old" or "new"
    
    # Calculated values
    total_income = Column(Float)
    total_deductions = Column(Float)
    taxable_income = Column(Float)
    tax_amount = Column(Float)
    
    status = Column(String(20), default="draft")  # draft, submitted, approved
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    employee = relationship("User", backref="tax_declarations")


class TaxSlabs(Base):
    """Tax slab configuration"""
    __tablename__ = "tax_slabs"
    
    id = Column(Integer, primary_key=True, index=True)
    financial_year = Column(String(10), nullable=False)
    tax_regime = Column(String(20), nullable=False)  # "old" or "new"
    
    min_income = Column(Float, nullable=False)
    max_income = Column(Float, nullable=True)  # NULL for highest slab
    tax_rate = Column(Float, nullable=False)  # Percentage
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())