"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # Database configuration
    # Ensure absolute path to avoid confusion between backend/instance and root/instance
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DB_PATH = os.path.join(BASE_DIR, 'instance', 'paraditi.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # ML Configuration
    ML_MODEL_NAME = os.getenv('ML_MODEL_NAME', 'all-MiniLM-L6-v2')
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.3'))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # API Setu (apisetu.gov.in) - Government scheme/API directory
    API_SETU_BASE_URL = os.getenv('API_SETU_BASE_URL', 'https://directory.apisetu.gov.in')
    API_SETU_CLIENT_ID = os.getenv('API_SETU_CLIENT_ID', 'your_client_id_here') # Placeholder for Step 1
    API_SETU_CLIENT_SECRET = os.getenv('API_SETU_CLIENT_SECRET', 'your_client_secret_here') # Placeholder for Step 1
    API_SETU_API_KEY = os.getenv('API_SETU_API_KEY', '')
    API_SETU_FEED_URL = os.getenv('API_SETU_FEED_URL', '')  # Optional bulk JSON feed URL
    API_SETU_SYNC_TAG = os.getenv('API_SETU_SYNC_TAG', 'Gov')
    API_SETU_SYNC_LIMIT = int(os.getenv('API_SETU_SYNC_LIMIT', '100'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
