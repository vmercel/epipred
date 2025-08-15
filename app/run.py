#!/usr/bin/env python3
"""
EpiPred Web Application Launcher
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the Flask app for WSGI deployment
try:
    from app import app
    logger.info("Flask app imported successfully for WSGI deployment")
except ImportError as e:
    logger.error(f"Failed to import Flask app: {e}")
    # Create a dummy app for error handling
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Import Error: {e}", 500

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask',
        'tensorflow',
        'numpy',
        'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install dependencies with: pip install -r requirements.txt")
        return False
    
    return True

def check_model_files():
    """Check if model files exist"""
    model_paths = [
        'models/epitope_model.keras',
        'models/epitope_model.h5',
        'models/epitope_model_savedmodel',
        '../epitope_model.keras',
        '../epitope_model.h5',
        '../epitope_model_savedmodel',
        'epitope_model.keras',
        'epitope_model.h5',
        'epitope_model_savedmodel'
    ]
    
    for path in model_paths:
        if os.path.exists(path):
            logger.info(f"Found model file: {path}")
            return True
    
    logger.warning("No model files found. Please ensure model files are available.")
    logger.warning("Expected locations: models/ directory or current directory")
    return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'static/uploads',
        'static/css',
        'static/js',
        'templates',
        'models'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def main():
    """Main function to start the application"""
    logger.info("Starting EpiPred Web Application...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check model files
    if not check_model_files():
        logger.warning("Continuing without model files - predictions may fail")
    
    # Create directories
    create_directories()
    
    # Configuration
    app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=app.config['DEBUG'],
        threaded=True
    )

if __name__ == '__main__':
    main()
