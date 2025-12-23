"""
Application settings and configuration.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///travellr.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis/Cache
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION = 3600  # 1 hour
    
    # Payment Gateway
    STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    
    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URL", "sqlite:///travellr_dev.db")


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
