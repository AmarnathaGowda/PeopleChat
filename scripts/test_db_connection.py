"""
Test database connection and models
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.database import engine, SessionLocal
from models.user import User
from models.leave import LeaveRequest
from models.tax import TaxDeclaration
from models.conversation import ChatSession
from utils.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def test_connection():
    """Test basic database connection"""
    try:
        with engine.connect() as conn:
            # Use text() for raw SQL in SQLAlchemy 2.0
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def test_models():
    """Test model queries"""
    db = SessionLocal()
    try:
        # Test user query
        user_count = db.query(User).count()
        logger.info(f"Found {user_count} users in database")
        
        # List all users
        users = db.query(User).all()
        for user in users:
            logger.info(f"User: {user.employee_id} - {user.full_name} ({user.role})")
        
        # Test other models
        leave_count = db.query(LeaveRequest).count()
        logger.info(f"Found {leave_count} leave requests")
        
        tax_count = db.query(TaxDeclaration).count()
        logger.info(f"Found {tax_count} tax declarations")
        
        session_count = db.query(ChatSession).count()
        logger.info(f"Found {session_count} chat sessions")
        
        return True
        
    except Exception as e:
        logger.error(f"Model query failed: {e}")
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    logger.info("Starting database tests...")
    
    if not test_connection():
        logger.error("Connection test failed, exiting")
        return
    
    if not test_models():
        logger.error("Model tests failed")
        return
    
    logger.info("All database tests passed!")


if __name__ == "__main__":
    main()