"""
Application Configuration

Centralized configuration management using environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "WC26 Intelligence Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://wc26:wc26pass@localhost:5432/wc26_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # ML Configuration
    MODEL_VERSION: str = "v1.0.0"
    MODEL_PATH: str = "../ml/models"
    SHAP_ENABLED: bool = True
    FEATURE_CACHE_ENABLED: bool = True
    
    # Simulation
    MONTE_CARLO_ITERATIONS: int = 10000
    SIMULATION_CACHE_TTL: int = 3600
    
    # Scoring System
    POINTS_CORRECT_RESULT: int = 3
    POINTS_EXACT_SCORE: int = 5
    POINTS_CORRECT_WINNER: int = 2
    POINTS_UPSET_BONUS: int = 2
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # MLflow (optional)
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
