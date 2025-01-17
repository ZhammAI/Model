# backend/src/utils/config.py

import os
from typing import Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Zham AI Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API Settings
    API_PREFIX: str = "/api"
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "Zham AI"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS Settings
    CORS_ORIGINS: str = "*"  # Comma-separated origins in production
    CORS_CREDENTIALS: bool = True

    # Database Settings
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/zhamdb"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = None
    REDIS_POOL_SIZE: int = 10

    # JWT Settings
    JWT_SECRET: str = "your-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Twitter API Settings
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_BEARER_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN_SECRET: str = ""

    # Solana RPC Settings
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    SOLANA_WS_URL: str = "wss://api.mainnet-beta.solana.com"

    # Cache Settings
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_PREFIX: str = "zham:"

    # WebSocket Settings
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_HEARTBEAT_INTERVAL: int = 30

    # Meta Analysis Settings
    META_UPDATE_INTERVAL: int = 300  # 5 minutes
    MIN_TOKEN_VOLUME: float = 10000.0
    MIN_HOLDERS_COUNT: int = 100
    SENTIMENT_THRESHOLD: float = 0.6

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_cors_origins(self) -> list:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return self.CORS_ORIGINS.split(",")

    @property
    def api_url(self) -> str:
        return f"{self.API_PREFIX}{self.API_V1_STR}"

    def get_db_connection_params(self) -> Dict[str, Any]:
        return {
            "database_url": self.DATABASE_URL,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW
        }

    def get_redis_connection_params(self) -> Dict[str, Any]:
        return {
            "url": self.REDIS_URL,
            "password": self.REDIS_PASSWORD,
            "pool_size": self.REDIS_POOL_SIZE
        }

    def get_jwt_settings(self) -> Dict[str, Any]:
        return {
            "secret_key": self.JWT_SECRET,
            "algorithm": self.JWT_ALGORITHM,
            "expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES
        }

    def get_twitter_credentials(self) -> Dict[str, str]:
        return {
            "api_key": self.TWITTER_API_KEY,
            "api_secret": self.TWITTER_API_SECRET,
            "bearer_token": self.TWITTER_BEARER_TOKEN,
            "access_token": self.TWITTER_ACCESS_TOKEN,
            "access_token_secret": self.TWITTER_ACCESS_TOKEN_SECRET
        }

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to prevent multiple reads of environment variables.
    """
    return Settings()

# Create a global settings instance
settings = get_settings()