# Reset database script
Write-Host "=== MeetMate Database Reset Tool ===" -ForegroundColor Cyan

# Stop any running Python processes
Write-Host "Stopping any running Python processes..."
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Set variables
$instanceDir = ".\instance"
$dbPath = "$instanceDir\meetmate.db"

# Create instance directory if it doesn't exist
if (-not (Test-Path $instanceDir)) {
    Write-Host "Creating instance directory..."
    New-Item -ItemType Directory -Path $instanceDir -Force | Out-Null
}

# Check directory permissions
$acl = Get-Acl $instanceDir
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("EVERYONE","FullControl","Allow")
$acl.SetAccessRule($accessRule)
Set-Acl $instanceDir $acl
Write-Host "Updated directory permissions for $instanceDir" -ForegroundColor Green

# Backup existing database if it exists
if (Test-Path $dbPath) {
    $backupPath = "$dbPath.bak"
    Write-Host "Backing up existing database to $backupPath"
    
    # Remove old backup if it exists
    if (Test-Path $backupPath) {
        Remove-Item -Path $backupPath -Force
    }
    
    # Rename current database as backup
    Rename-Item -Path $dbPath -NewName "$dbPath.bak" -Force
    Write-Host "Removed old database file"
}

# Initialize the database using our direct initialization script
Write-Host "Initializing new database..." -ForegroundColor Cyan
try {
    # First try the direct DB initialization
    Write-Host "Running direct database initialization..."
    python direct_db_init.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database initialized successfully!" -ForegroundColor Green
        
        # Verify database
        if (Test-Path $dbPath) {
            $dbSize = (Get-Item $dbPath).Length
            Write-Host "Database file size: $dbSize bytes"
        } else {
            Write-Host "WARNING: Database file wasn't created!" -ForegroundColor Red
            exit 1
        }
    } else {
        throw "Database initialization failed with direct method. Exit code: $LASTEXITCODE"
    }
}
catch {
    Write-Host "Error initializing database: $_" -ForegroundColor Red
    exit 1
}

Write-Host "=== Database Reset Complete ===" -ForegroundColor Cyan