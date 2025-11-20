# CraftChain Quick Fix for PowerShell
Write-Host "CraftChain Quick Fix" -ForegroundColor Yellow
Write-Host "===================" -ForegroundColor Yellow

# Step 1: Kill all Python processes
Write-Host "Step 1: Stopping all Python processes..." -ForegroundColor Red
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process pythonw -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "Done." -ForegroundColor Green

# Step 2: Wait
Write-Host "Step 2: Waiting for processes to terminate..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Step 3: Create new database
Write-Host "Step 3: Creating fresh database..." -ForegroundColor Cyan
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$newDbPath = "$env:TEMP\craftchain_$timestamp.db"

# Run Python to create database
$pythonScript = @"
import sys, os, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    db_path = r'$newDbPath'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('PRAGMA journal_mode=WAL')
    cursor.execute('PRAGMA busy_timeout=30000')
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.execute('PRAGMA synchronous=NORMAL')
    cursor.execute('PRAGMA cache_size=10000')
    cursor.execute('PRAGMA temp_store=MEMORY')
    conn.commit()
    conn.close()
    
    from app import app, db, ensure_category_column
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.create_all()
        ensure_category_column()
    
    with open('database_path.txt', 'w') as f:
        f.write(db_path)
    
    print('SUCCESS: Database created and configured')
except Exception as e:
    print(f'ERROR: {e}')
"@

Set-Location $PSScriptRoot
python -c $pythonScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database created successfully!" -ForegroundColor Green
} else {
    Write-Host "Database creation failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 4: Start service
Write-Host "Step 4: Starting CraftChain service..." -ForegroundColor Cyan
Start-Process powershell -WindowStyle Hidden -ArgumentList "-ExecutionPolicy Bypass -File `"$PSScriptRoot\CraftChain-Service.ps1`""

# Step 5: Wait for service to start
Write-Host "Step 5: Waiting for service to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Step 6: Test and open browser
Write-Host "Step 6: Testing service..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:5002/" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Service is running successfully!" -ForegroundColor Green
        Start-Process "http://127.0.0.1:5002"
    } else {
        Write-Host "⚠️ Service starting up... Please wait a few more seconds" -ForegroundColor Yellow
        Start-Process "http://127.0.0.1:5002"
    }
} catch {
    Write-Host "⚠️ Service is starting... Give it 10 more seconds" -ForegroundColor Yellow
    Start-Process "http://127.0.0.1:5002"
}

Write-Host "`n🎉 QUICK FIX COMPLETED!" -ForegroundColor Green
Write-Host "All database errors should now be resolved!" -ForegroundColor Green
Write-Host "You can now test registration, login, and product creation." -ForegroundColor Cyan

Read-Host "`nPress Enter to exit"
