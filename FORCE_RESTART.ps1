# CraftChain Force Restart Script
# This script forcefully restarts the service bypassing all locks

Write-Host "CraftChain Force Restart" -ForegroundColor Yellow
Write-Host "=========================" -ForegroundColor Yellow

# Kill all Python processes
Write-Host "Stopping all Python processes..." -ForegroundColor Red
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process pythonw -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait for processes to die
Start-Sleep -Seconds 3

# Run the Ultimate Fix
Write-Host "Running Ultimate Database Fix..." -ForegroundColor Green
& "$PSScriptRoot\ULTIMATE_FIX.bat"

Write-Host "Force restart completed!" -ForegroundColor Green
Write-Host "Please wait 10-20 seconds for the service to start." -ForegroundColor Cyan

# Open the browser after a delay
Start-Sleep -Seconds 10
Start-Process "http://127.0.0.1:5002"
