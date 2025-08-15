#!/usr/bin/env python3
"""
Configuration settings for EpiPred deployment
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    
    # Model configuration
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'models'
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', '0.5'))
    
    # Performance settings
    MAX_SEQUENCES = int(os.environ.get('MAX_SEQUENCES', '50'))
    MAX_TOTAL_LENGTH = int(os.environ.get('MAX_TOTAL_LENGTH', '300000'))
    MAX_SEQUENCE_LENGTH = int(os.environ.get('MAX_SEQUENCE_LENGTH', '6000'))
    MIN_SEQUENCE_LENGTH = int(os.environ.get('MIN_SEQUENCE_LENGTH', '10'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Use environment variables for production
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class RenderConfig(ProductionConfig):
    """Render.com specific configuration"""
    # Render-specific settings
    PORT = int(os.environ.get('PORT', 5000))
    HOST = '0.0.0.0'
    
    # Use /tmp for uploads on Render
    UPLOAD_FOLDER = '/tmp/uploads'
    
    # Reduced limits for free tier
    MAX_SEQUENCES = 25
    MAX_TOTAL_LENGTH = 150000

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'render': RenderConfig,
    'default': DevelopmentConfig
}
