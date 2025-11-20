@echo off
title CraftChain Quick Fix
echo ========================================
echo CraftChain Quick Fix Tool
echo ========================================
echo.

echo Step 1: Stopping all Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo Done.

echo.
echo Step 2: Waiting for processes to terminate...
timeout /t 3 /nobreak >nul
echo Done.

echo.
echo Step 3: Force fixing database...
python force_fix_database.py
echo.

echo Step 4: Starting CraftChain service...
echo Starting service in background...
start /MIN "" powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0CraftChain-Service.ps1"

echo.
echo ========================================
echo Fix completed!
echo.
echo The CraftChain service should now be running.
echo Look for the CraftChain icon in your system tray.
echo.
echo You can now try:
echo - Registering new users
echo - Logging in
echo - Adding products
echo.
echo ========================================
pause
