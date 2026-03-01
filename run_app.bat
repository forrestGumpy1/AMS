@echo off
echo.
echo =========================================
echo Attendance Management System - Start
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Could not activate virtual environment
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error: Could not install dependencies
    pause
    exit /b 1
)

echo.
echo =========================================
echo Database Initialization
echo =========================================
echo.
echo Do you want to initialize the database with sample data?
echo (This will create test admin and user accounts)
set /p init="Initialize? (y/n): "

if /i "%init%"=="y" (
    python init_db.py
    if errorlevel 1 (
        echo Warning: Database initialization had issues
    )
) else (
    echo Skipping database initialization
    echo You will need to create admin and user accounts manually
)

echo.
echo =========================================
echo Starting Application
echo =========================================
echo.
echo Application URL: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
