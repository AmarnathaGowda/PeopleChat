"""
Central configuration management for the Agentic RAG Chatbot
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "PeopleChat (Agentic RAG Chatbot)"
    app_version: str = "0.0.001"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Security
    secret_key: str = "your-secret-key-here"  # Change in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-ada-002"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Azure Settings
    azure_subscription_id: Optional[str] = None
    azure_resource_group: Optional[str] = None
    azure_cognitive_search_endpoint: Optional[str] = None
    azure_cognitive_search_key: Optional[str] = None
    azure_cognitive_search_index: str = "hr-policies"
    
    # Database
    database_url: str = "mssql+pymssql://username:password@server/database"
    db_echo: bool = False
    
    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    cache_ttl: int = 300  # 5 minutes default
    
    # External APIs
    leave_management_api_url: str = ""
    leave_management_api_key: str = ""
    salary_api_url: str = ""
    salary_api_key: str = ""
    tax_api_url: str = ""
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 5
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> settings:
    """Get cached settings instance"""
    return settings()


# Create a settings instance
settings = get_settings()