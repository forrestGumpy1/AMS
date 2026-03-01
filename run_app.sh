#!/bin/bash

echo ""
echo "========================================="
echo "Attendance Management System - Start"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Could not activate virtual environment"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Could not install dependencies"
    exit 1
fi

echo ""
echo "========================================="
echo "Database Initialization"
echo "========================================="
echo ""
read -p "Initialize database with sample data? (y/n): " init

if [ "$init" = "y" ] || [ "$init" = "Y" ]; then
    python3 init_db.py
    if [ $? -ne 0 ]; then
        echo "Warning: Database initialization had issues"
    fi
else
    echo "Skipping database initialization"
    echo "You will need to create admin and user accounts manually"
fi

echo ""
echo "========================================="
echo "Starting Application"
echo "========================================="
echo ""
echo "Application URL: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
