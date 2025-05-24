# MeetMate Application Launcher
# This script helps you start the MeetMate application

Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "MeetMate Application Launcher" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

function Show-Menu {
    Write-Host ""
    Write-Host "Choose an option:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Start MeetMate Application" -ForegroundColor Green
    Write-Host "   - Beginner-friendly Flask app"
    Write-Host "   - Uses SQLite3 with raw SQL"
    Write-Host "   - Perfect for learning"
    Write-Host ""
    Write-Host "2. View Documentation" -ForegroundColor Magenta
    Write-Host "3. Reset Database" -ForegroundColor Red
    Write-Host "4. Exit" -ForegroundColor Gray
    Write-Host ""
}

function Start-Application {
    Write-Host "Starting MeetMate Application..." -ForegroundColor Green
    Write-Host "This version uses Python's built-in sqlite3 module" -ForegroundColor White
    Write-Host "Database operations are clearly visible in the code" -ForegroundColor White
    Write-Host ""
    Write-Host "Visit: http://127.0.0.1:5000" -ForegroundColor Cyan
    Write-Host "Default admin login: admin / admin123" -ForegroundColor Yellow
    Write-Host ""
    python app_beginner.py
}

function Show-Documentation {
    Write-Host "Opening documentation..." -ForegroundColor Magenta
    Write-Host ""
    if (Test-Path "README.md") {
        Get-Content "README.md" | Select-Object -First 30
        Write-Host ""
        Write-Host "📖 Available Documentation:" -ForegroundColor Cyan
        Write-Host "  - README.md          - Main application guide" -ForegroundColor White
        Write-Host "  - QUICK_START.md     - 3-step setup guide" -ForegroundColor White
        Write-Host "  - COMPARISON.md      - Technical comparison" -ForegroundColor White
    } else {
        Write-Host "Documentation not found" -ForegroundColor Red
    }
}

function Reset-Database {
    Write-Host "Resetting database..." -ForegroundColor Red
    Write-Host "Deleting existing database..." -ForegroundColor Yellow
    
    if (Test-Path "instance\meetmate.db") {
        Remove-Item "instance\meetmate.db" -Force
        Write-Host "✅ Database deleted successfully" -ForegroundColor Green
        Write-Host "The application will recreate it with default data on next start" -ForegroundColor White
    } else {
        Write-Host "⚠️  Database file not found" -ForegroundColor Yellow
    }
}

# Interactive menu only
while ($true) {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-4)"    
    switch ($choice) {
        "1" { 
            Start-Application
            break
        }
        "2" { 
            Show-Documentation
            Write-Host ""
            Write-Host "Press any key to continue..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "3" { 
            Reset-Database
            Write-Host ""
            Write-Host "Press any key to continue..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "4" { 
            Write-Host "Goodbye!" -ForegroundColor Yellow
            exit 
        }
        default { 
            Write-Host "Invalid choice. Please enter 1-4." -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}
