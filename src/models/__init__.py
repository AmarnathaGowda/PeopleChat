"""
Models package initialization
Import all models to ensure they are registered with SQLAlchemy
"""
# Import Base and database utilities first
from models.database import Base, get_db, init_db, engine

# Import all models to register them with SQLAlchemy
from models.user import User, UserRole
from models.conversation import ChatSession, Message
from models.leave import LeaveRequest, LeaveBalance, LeaveType, LeaveStatus
from models.tax import TaxDeclaration, TaxSlabs
from models.audit import AuditLog

# Force model registration
__all__ = [
    "Base",
    "get_db",
    "init_db",
    "engine",
    "User",
    "UserRole",
    "ChatSession",
    "Message",
    "LeaveRequest",
    "LeaveBalance",
    "LeaveType",
    "LeaveStatus",
    "TaxDeclaration",
    "TaxSlabs",
    "AuditLog"
]

# This ensures all models are loaded
print(f"Loaded models: {[table.name for table in Base.metadata.tables.values()]}")