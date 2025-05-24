# MeetMate Version Switcher
# This script helps you run different versions of the MeetMate application

param(
    [Parameter(Mandatory=$false)]
    [string]$Version = "menu"
)

Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host "MeetMate Application Launcher" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

function Show-Menu {
    Write-Host ""
    Write-Host "Choose which version to run:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Beginner-Friendly Version (SQLite3)" -ForegroundColor Green
    Write-Host "   - Uses raw SQL queries"
    Write-Host "   - Perfect for learning"
    Write-Host "   - Detailed comments"
    Write-Host ""
    Write-Host "2. Original Version (SQLAlchemy)" -ForegroundColor Blue
    Write-Host "   - Uses ORM (Object-Relational Mapping)"
    Write-Host "   - More advanced"
    Write-Host "   - Industry standard"
    Write-Host ""
    Write-Host "3. View Comparison Guide" -ForegroundColor Magenta
    Write-Host "4. Reset Database" -ForegroundColor Red
    Write-Host "5. Exit" -ForegroundColor Gray
    Write-Host ""
}

function Start-BeginnerVersion {
    Write-Host "Starting Beginner-Friendly Version..." -ForegroundColor Green
    Write-Host "This version uses Python's built-in sqlite3 module" -ForegroundColor White
    Write-Host "Database operations are clearly visible in the code" -ForegroundColor White
    Write-Host ""
    python app_beginner.py
}

function Start-OriginalVersion {
    Write-Host "Starting Original Version..." -ForegroundColor Blue
    Write-Host "This version uses SQLAlchemy ORM" -ForegroundColor White
    Write-Host "More abstracted but production-ready" -ForegroundColor White
    Write-Host ""
    python app.py
}

function Show-Comparison {
    Write-Host "Opening comparison guide..." -ForegroundColor Magenta
    if (Test-Path "COMPARISON.md") {
        Get-Content "COMPARISON.md" | Select-Object -First 50
        Write-Host ""
        Write-Host "Full comparison guide is in COMPARISON.md" -ForegroundColor Cyan
        Write-Host "Beginner guide is in README_beginner.md" -ForegroundColor Cyan
    } else {
        Write-Host "Comparison guide not found" -ForegroundColor Red
    }
}

function Reset-Database {
    Write-Host "Resetting database..." -ForegroundColor Red
    if (Test-Path ".\reset_db.ps1") {
        .\reset_db.ps1
    } else {
        Write-Host "Database reset script not found" -ForegroundColor Red
    }
}

# Handle command line parameter
switch ($Version.ToLower()) {
    "beginner" { Start-BeginnerVersion; return }
    "original" { Start-OriginalVersion; return }
    "comparison" { Show-Comparison; return }
    "reset" { Reset-Database; return }
}

# Interactive menu
while ($true) {
    Show-Menu
    $choice = Read-Host "Enter your choice (1-5)"
    
    switch ($choice) {
        "1" { 
            Start-BeginnerVersion
            break
        }
        "2" { 
            Start-OriginalVersion
            break
        }
        "3" { 
            Show-Comparison
            Write-Host ""
            Write-Host "Press any key to continue..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "4" { 
            Reset-Database
            Write-Host ""
            Write-Host "Press any key to continue..." -ForegroundColor Gray
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }
        "5" { 
            Write-Host "Goodbye!" -ForegroundColor Yellow
            exit 
        }
        default { 
            Write-Host "Invalid choice. Please enter 1-5." -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}
