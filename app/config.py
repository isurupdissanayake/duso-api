from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv
from typing import Optional, Set, Dict, Any, List
import os
from enum import Enum
import secrets
from functools import lru_cache

# Load environment variables
load_dotenv()

class Environment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment (development/production)"
    )
    
    # Application Settings
    PROJECT_NAME: str = "Duso API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # File Storage Settings
    FILE_STORAGE_PATH: str = Field(default="./data", env="FILE_STORAGE_PATH")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="info", env="LOG_LEVEL")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # MongoDB Settings
    MONGODB_URL: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    MONGODB_DB_NAME: str = Field(default="duso_db", env="MONGODB_DB_NAME")
    MONGODB_MAX_POOL_SIZE: int = Field(default=100, env="MONGODB_MAX_POOL_SIZE")
    MONGODB_MIN_POOL_SIZE: int = Field(default=10, env="MONGODB_MIN_POOL_SIZE")
    
    # Security Settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Cookie Settings
    COOKIE_SECURE: bool = Field(default=True, env="COOKIE_SECURE")
    COOKIE_SAMESITE: str = Field(default="lax", env="COOKIE_SAMESITE")
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["*"],
        description="List of allowed origins for CORS"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    @field_validator("ENVIRONMENT", mode='before')
    @classmethod
    def validate_environment(cls, v: str) -> Environment:
        """Validate environment value"""
        try:
            return Environment(v.lower())
        except ValueError:
            raise ValueError(f"Invalid environment: {v}. Must be one of {[e.value for e in Environment]}")
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    def get_environment_specific_settings(self) -> Dict[str, Any]:
        """Get environment-specific settings"""
        if self.is_development:
            return {
                "DEBUG": True,
                "LOG_LEVEL": "debug",
                "MONGODB_MAX_POOL_SIZE": 50,
                "RATE_LIMIT_PER_MINUTE": 100,
                "BACKEND_CORS_ORIGINS": ["*"],
                "COOKIE_SECURE": False,
                "COOKIE_SAMESITE": "lax"
            }
        return {
            "DEBUG": False,
            "LOG_LEVEL": "info",
            "MONGODB_MAX_POOL_SIZE": 100,
            "RATE_LIMIT_PER_MINUTE": 60,
            "BACKEND_CORS_ORIGINS": [],  # Should be configured in production env file
            "COOKIE_SECURE": True,
            "COOKIE_SAMESITE": "strict"
        }
    
    model_config = {
        "env_file": "env/development.env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
