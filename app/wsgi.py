#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set up logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the Flask app
try:
    from app import app
    
    # Configure for production
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # Create upload directory
    upload_dir = app.config.get('UPLOAD_FOLDER', 'static/uploads')
    if upload_dir.startswith('/tmp'):
        # For platforms like Render that use /tmp
        os.makedirs(upload_dir, exist_ok=True)
    else:
        # For local deployment
        os.makedirs(upload_dir, exist_ok=True)
    
    logging.info("EpiPred application initialized successfully")
    
except Exception as e:
    logging.error(f"Failed to initialize application: {e}")
    raise

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
