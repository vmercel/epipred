#!/bin/bash

# EpiPred Web Application Startup Script

echo "Starting EpiPred Web Application..."
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed or not in PATH"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running application tests..."
python test_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Tests passed! Starting the application..."
    echo ""
    echo "The application will be available at: http://localhost:5000"
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the application
    python run.py
else
    echo ""
    echo "Tests failed. Please check the errors above."
    echo "You can still try to start the application with: python run.py"
fi
