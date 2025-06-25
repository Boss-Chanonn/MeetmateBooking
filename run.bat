@echo off
echo Starting MeetMate Application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Start the Flask application
echo Starting Flask server...
echo Open your browser to: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause