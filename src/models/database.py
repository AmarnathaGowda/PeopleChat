"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging
import urllib.parse

from config.config import settings

logger = logging.getLogger(__name__)

# URL decode the password if needed
db_url = settings.database_url
if 'pyodbc' in db_url:
    # Handle special characters in password for pyodbc
    parts = db_url.split('@')
    if len(parts) > 1:
        # Extract and decode password
        cred_part = parts[0].split('://')[-1]
        if ':' in cred_part:
            user, password = cred_part.split(':', 1)
            # URL decode the password
            password = urllib.parse.unquote(password)
            # Rebuild the URL with decoded password
            db_url = db_url.replace(f":{urllib.parse.quote(password)}@", f":{password}@")

# Create database engine
engine = create_engine(
    db_url,
    echo=settings.db_echo,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise