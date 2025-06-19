"""
Initialize database with tables and seed data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.database import init_db, engine, Base, SessionLocal
from models.user import User, UserRole
from models.tax import TaxSlabs
from utils.security import hash_password
from utils.logger import setup_logging, get_logger


# Setup logging
setup_logging()
logger = get_logger(__name__)


def create_sample_users(db):
    """Create sample users for testing"""
    users = [
        {
            "employee_id": "EMP001",
            "email": "admin@example.com",
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
            "department": "IT",
            "hashed_password": hash_password("admin123")
        },
        {
            "employee_id": "EMP002",
            "email": "manager@example.com",
            "full_name": "Manager User",
            "role": UserRole.MANAGER,
            "department": "Engineering",
            "hashed_password": hash_password("manager123")
        },
        {
            "employee_id": "EMP003",
            "email": "employee@example.com",
            "full_name": "Employee User",
            "role": UserRole.EMPLOYEE,
            "department": "Engineering",
            "manager_id": 2,  # Reports to manager
            "hashed_password": hash_password("employee123")
        }
    ]
    
    for user_data in users:
        # Handle manager_id separately
        manager_id = user_data.pop("manager_id", None)
        user = User(**user_data)
        db.add(user)
        db.flush()  # Flush to get the ID
        
        # Update manager_id after users are created
        if manager_id and user.employee_id == "EMP003":
            user.manager_id = manager_id
    
    db.commit()
    logger.info(f"Created {len(users)} sample users")


def create_tax_slabs(db):
    """Create tax slab data for 2023-24"""
    # Old regime slabs
    old_regime_slabs = [
        {"min_income": 0, "max_income": 250000, "tax_rate": 0},
        {"min_income": 250001, "max_income": 500000, "tax_rate": 5},
        {"min_income": 500001, "max_income": 1000000, "tax_rate": 20},
        {"min_income": 1000001, "max_income": None, "tax_rate": 30}
    ]
    
    # New regime slabs
    new_regime_slabs = [
        {"min_income": 0, "max_income": 300000, "tax_rate": 0},
        {"min_income": 300001, "max_income": 600000, "tax_rate": 5},
        {"min_income": 600001, "max_income": 900000, "tax_rate": 10},
        {"min_income": 900001, "max_income": 1200000, "tax_rate": 15},
        {"min_income": 1200001, "max_income": 1500000, "tax_rate": 20},
        {"min_income": 1500001, "max_income": None, "tax_rate": 30}
    ]
    
    # Add old regime slabs
    for slab_data in old_regime_slabs:
        slab = TaxSlabs(
            financial_year="2023-24",
            tax_regime="old",
            **slab_data
        )
        db.add(slab)
    
    # Add new regime slabs
    for slab_data in new_regime_slabs:
        slab = TaxSlabs(
            financial_year="2023-24",
            tax_regime="new",
            **slab_data
        )
        db.add(slab)
    
    db.commit()
    logger.info("Created tax slab data")


def main():
    """Initialize database with tables and seed data"""
    logger.info("Starting database initialization...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Create seed data
        db = SessionLocal()
        
        try:
            # Check if data already exists
            existing_users = db.query(User).count()
            if existing_users == 0:
                create_sample_users(db)
                create_tax_slabs(db)
                logger.info("Seed data created successfully")
            else:
                logger.info("Database already contains data, skipping seed data")
                
        finally:
            db.close()
            
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()