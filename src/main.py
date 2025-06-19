"""
Main FastAPI application entry point
"""
import sys
import logging
from contextlib import asynccontextmanager

# Python version check
if sys.version_info < (3, 11):
    raise RuntimeError("Python 3.11 or higher is required")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from config.config import settings
from models.database import init_db
from utils.logger import setup_logging, get_logger

# Setup structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API running at http://{settings.api_host}:{settings.api_port}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't raise in development to allow API to start
        if settings.environment == "production":
            raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready multi-agent chatbot with RAG capabilities for leave management, IT declarations, and HR policy Q&A",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Welcome message
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "Visit /docs for API documentation"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment
    }
    
    # Check database connectivity
    try:
        from models.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Use text() for SQLAlchemy 2.0 compatibility
            result = conn.execute(text("SELECT 1"))
            result.fetchone()  # Fetch the result
            
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/debug/settings", tags=["Debug"])
async def debug_settings():
    """
    Debug endpoint to check current settings
    
    **Note**: This endpoint should be removed or protected in production
    """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "environment": settings.environment,
        "docs_enabled": app.docs_url is not None,
        "api_prefix": settings.api_prefix,
        "cors_origins": settings.cors_origins,
        "log_level": settings.log_level,
        "openai_model": settings.openai_model,
        "cache_ttl": settings.cache_ttl,
        "rate_limit": {
            "requests": settings.rate_limit_requests,
            "period": settings.rate_limit_period
        }
    }


@app.get("/api/v1/info", tags=["API Info"])
async def api_info():
    """
    API information endpoint
    """
    from models.database import SessionLocal
    from models.user import User
    
    # Get some basic stats
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
    except:
        user_count = 0
    finally:
        db.close()
    
    return {
        "api_version": "v1",
        "total_users": user_count,
        "agents": [
            {
                "name": "Leave Management Agent",
                "status": "pending",
                "capabilities": ["apply_leave", "approve_leave", "check_status"]
            },
            {
                "name": "IT Declaration Adviser",
                "status": "pending",
                "capabilities": ["tax_calculation", "regime_comparison", "optimization"]
            },
            {
                "name": "HR Policy Q&A",
                "status": "pending",
                "capabilities": ["policy_search", "contextual_answers", "document_retrieval"]
            }
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "metrics": "/metrics"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
        access_log=True
    )