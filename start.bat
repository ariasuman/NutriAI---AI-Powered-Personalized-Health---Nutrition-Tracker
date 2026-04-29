@echo off
echo Health & Nutrition Tracker - Quick Start
echo ========================================

REM Try different Python commands
py --version >nul 2>&1
if not errorlevel 1 (
    echo Found Python via 'py' command
    py setup.py
    pause
    py import_foods.py
    pause
    py run.py
    goto :end
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    echo Found Python via 'python3' command
    python3 setup.py
    pause
    python3 import_foods.py
    pause
    python3 run.py
    goto :end
)

python --version >nul 2>&1
if not errorlevel 1 (
    echo Found Python via 'python' command
    python setup.py
    pause
    python import_foods.py
    pause
    python run.py
    goto :end
)

echo ERROR: Python not found in PATH
echo Please install Python 3.11+ from https://python.org
echo Make sure to check "Add Python to PATH" during installation
pause

:end