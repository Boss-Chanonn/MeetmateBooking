# Initializes database schema and runs the application
# Ensure this script is run in the project directory

Write-Host "Initializing database and starting MeetMate..."

# Activate the virtual environment
if (Test-Path ".venv\Scripts\activate.ps1") {
    . .\.venv\Scripts\activate.ps1
    Write-Host "Activated virtual environment"
} else {
    Write-Host "Virtual environment not found. Installing dependencies globally..."
}

# Ensure dependencies are installed
pip install -r requirements.txt
Write-Host "Dependencies installed"

# Check database schema
Write-Host "Checking database schema..."
python update_schema.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Database schema issues detected." -ForegroundColor Yellow
    $choice = Read-Host "Do you want to reset the database? (y/n)"
    if ($choice -eq "y") {
        Write-Host "Running database reset..."
        .\reset_db.ps1
    } else {
        Write-Host "Warning: The application may not run correctly without fixing the database!" -ForegroundColor Red
    }
}

# Run the application
Write-Host "Starting MeetMate application..." -ForegroundColor Green
python app.py

Write-Host "Application stopped."
