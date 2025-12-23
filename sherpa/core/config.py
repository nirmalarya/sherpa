"""
SHERPA V1 - Environment Configuration
Supports dev/staging/production environments with appropriate settings
"""

import os
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Environment(str, Enum):
    """Supported environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentConfig(BaseModel):
    """Configuration for a specific environment"""
    environment: Environment
    debug: bool
    log_level: str
    cors_origins: list[str]
    api_rate_limit: int
    api_rate_window: int
    database_path: str

    class Config:
        use_enum_values = True


# Environment-specific configurations
ENVIRONMENT_CONFIGS: Dict[Environment, EnvironmentConfig] = {
    Environment.DEVELOPMENT: EnvironmentConfig(
        environment=Environment.DEVELOPMENT,
        debug=True,
        log_level="DEBUG",
        cors_origins=[
            "http://localhost:3001",
            "http://localhost:3002",
            "http://localhost:3003",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002",
            "http://127.0.0.1:3003",
        ],
        api_rate_limit=100,
        api_rate_window=60,
        database_path="sherpa/data/sherpa.db"
    ),
    Environment.STAGING: EnvironmentConfig(
        environment=Environment.STAGING,
        debug=False,
        log_level="INFO",
        cors_origins=[
            "https://staging.sherpa.example.com",
            "http://localhost:3001",  # Allow local testing
        ],
        api_rate_limit=50,
        api_rate_window=60,
        database_path="sherpa/data/sherpa-staging.db"
    ),
    Environment.PRODUCTION: EnvironmentConfig(
        environment=Environment.PRODUCTION,
        debug=False,
        log_level="WARNING",
        cors_origins=[
            "https://sherpa.example.com",
            "https://app.sherpa.example.com",
        ],
        api_rate_limit=30,
        api_rate_window=60,
        database_path="sherpa/data/sherpa-production.db"
    )
}


class Settings:
    """Global settings with environment-based configuration"""

    def __init__(self):
        # Get environment from environment variable, default to development
        env_name = os.getenv("SHERPA_ENV", "development").lower()

        # Map environment string to Environment enum
        env_mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "staging": Environment.STAGING,
            "stage": Environment.STAGING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
        }

        self._environment = env_mapping.get(env_name, Environment.DEVELOPMENT)
        self._config = ENVIRONMENT_CONFIGS[self._environment]

    @property
    def environment(self) -> Environment:
        """Get current environment"""
        return self._environment

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self._environment == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode"""
        return self._environment == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self._environment == Environment.PRODUCTION

    @property
    def debug(self) -> bool:
        """Get debug mode setting"""
        return self._config.debug

    @property
    def log_level(self) -> str:
        """Get logging level"""
        return self._config.log_level

    @property
    def cors_origins(self) -> list[str]:
        """Get allowed CORS origins"""
        return self._config.cors_origins

    @property
    def api_rate_limit(self) -> int:
        """Get API rate limit (requests per window)"""
        return self._config.api_rate_limit

    @property
    def api_rate_window(self) -> int:
        """Get API rate limit window in seconds"""
        return self._config.api_rate_window

    @property
    def database_path(self) -> str:
        """Get database file path"""
        return self._config.database_path

    def get_config_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            "environment": self._environment.value,
            "debug": self.debug,
            "log_level": self.log_level,
            "cors_origins": self.cors_origins,
            "api_rate_limit": self.api_rate_limit,
            "api_rate_window": self.api_rate_window,
            "database_path": self.database_path,
        }

    def set_environment(self, env: str) -> None:
        """
        Set environment programmatically

        Args:
            env: Environment name (development, staging, production)
        """
        env_mapping = {
            "dev": Environment.DEVELOPMENT,
            "development": Environment.DEVELOPMENT,
            "staging": Environment.STAGING,
            "stage": Environment.STAGING,
            "prod": Environment.PRODUCTION,
            "production": Environment.PRODUCTION,
        }

        new_env = env_mapping.get(env.lower())
        if not new_env:
            raise ValueError(f"Invalid environment: {env}. Must be one of: development, staging, production")

        self._environment = new_env
        self._config = ENVIRONMENT_CONFIGS[new_env]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance"""
    return settings
