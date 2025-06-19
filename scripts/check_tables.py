"""
Check which tables exist and create missing ones
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

print(f"Current working directory: {Path(__file__).parent.parent / 'src'}")
print(f"Current working directory: {sys.path}")
from sqlalchemy import inspect, text
from models.database import engine, Base
from utils.logger import setup_logging, get_logger

# Import all models explicitly
from models.user import User
from models.conversation import ChatSession, Message
from models.leave import LeaveRequest, LeaveBalance
from models.tax import TaxDeclaration, TaxSlabs
from models.audit import AuditLog

# Setup logging
setup_logging()
logger = get_logger(__name__)


def check_existing_tables():
    """Check which tables already exist in the database"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    logger.info(f"Existing tables in database: {existing_tables}")
    return existing_tables


def check_models():
    """Check which models are registered with SQLAlchemy"""
    model_tables = list(Base.metadata.tables.keys())
    logger.info(f"Models registered with SQLAlchemy: {model_tables}")
    return model_tables


def create_missing_tables():
    """Create any missing tables"""
    existing = set(check_existing_tables())
    expected = set(Base.metadata.tables.keys())
    missing = expected - existing
    
    if missing:
        logger.info(f"Missing tables: {missing}")
        logger.info("Creating missing tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Missing tables created successfully")
    else:
        logger.info("All expected tables exist")


def main():
    """Main function"""
    logger.info("Checking database tables...")
    
    # Check what tables should exist
    logger.info("\n=== Expected Tables ===")
    expected_tables = check_models()
    
    # Check what tables actually exist
    logger.info("\n=== Existing Tables ===")
    existing_tables = check_existing_tables()
    
    # Create missing tables
    logger.info("\n=== Creating Missing Tables ===")
    create_missing_tables()
    
    # Verify all tables now exist
    logger.info("\n=== Final Table List ===")
    final_tables = check_existing_tables()
    logger.info(f"Total tables in database: {len(final_tables)}")


if __name__ == "__main__":
    main()