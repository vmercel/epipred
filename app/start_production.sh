#!/bin/bash
# Production startup script

# Set environment variables
export FLASK_ENV=production
export FLASK_APP=app.py

# Create necessary directories
mkdir -p static/uploads

# Start the application with Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --max-requests 1000 app:app
