@echo off
echo Health & Nutrition Tracker - Windows Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo Running setup script...
python setup.py

echo.
echo Setup complete! 
echo.
echo To start the application:
echo 1. Run: python import_foods.py (if you have the CSV file)
echo 2. Run: python run.py
echo.
pause