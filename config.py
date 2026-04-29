"""
Configuration module for ACEest Fitness Gym application.

This module defines all configuration settings for the Flask application,
including database settings, security settings, and environment-specific configs.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings."""

    # Flask settings
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "aceest_secret_key_dev")
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Database
    DATABASE = os.getenv("ACEEST_DB", "aceest_fitness.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload/File settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    PDF_FOLDER = os.path.join(UPLOAD_FOLDER, "reports")

    # Version
    VERSION = "0.1.0"

    # Pagination
    ITEMS_PER_PAGE = 10

    # Session
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DATABASE = "test_database.db"
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_database.db"
    WTF_CSRF_ENABLED = False


# Configuration selector
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(env=None):
    """
    Get configuration object based on environment.

    Args:
        env (str, optional): Environment name. Defaults to FLASK_ENV.

    Returns:
        Config: Configuration class instance.
    """
    if env is None:
        env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
