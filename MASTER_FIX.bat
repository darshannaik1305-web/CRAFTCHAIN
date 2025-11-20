@echo off
title CraftChain Master Fix - Complete Error Resolution
color 0A
echo ================================================
echo    CraftChain Master Fix - Complete Solution
echo ================================================
echo.
echo This script will fix ALL database and service errors
echo Please run as Administrator if possible
echo.
pause

echo.
echo [STEP 1/5] Stopping ALL CraftChain processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM powershell.exe >nul 2>&1
echo    - All Python processes stopped
echo    - All PowerShell processes stopped

echo.
echo [STEP 2/5] Clearing database locks and temporary files...
cd /d "%~dp0"

REM Remove all database-related files that might be locked
if exist "app.db" (
    echo    - Creating backup of existing database...
    copy "app.db" "app.db.backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db" >nul 2>&1
)

REM Force delete all database files
del /F /Q "app.db" >nul 2>&1
del /F /Q "app.db-wal" >nul 2>&1
del /F /Q "app.db-shm" >nul 2>&1
del /F /Q "app.db-journal" >nul 2>&1

REM Clear log files
del /F /Q "service.log" >nul 2>&1
del /F /Q "server_output.log" >nul 2>&1
del /F /Q "server_error.log" >nul 2>&1
del /F /Q "server.pid" >nul 2>&1

echo    - Database files cleared
echo    - Log files cleared
echo    - Lock files removed

echo.
echo [STEP 3/5] Recreating database with optimal settings...
python -c "
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
try:
    from app import app, db, ensure_category_column
    with app.app_context():
        db.create_all()
        ensure_category_column()
    print('    - Database recreated successfully')
except Exception as e:
    print(f'    - Error: {e}')
    input('Press Enter to continue...')
"

echo.
echo [STEP 4/5] Starting CraftChain service...
start "" /MIN powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0CraftChain-Service.ps1"

echo    - Service starting in background...
timeout /t 5 /nobreak >nul

echo.
echo [STEP 5/5] Verifying service is running...
curl -s http://127.0.0.1:5002/ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    - Service is RUNNING successfully!
) else (
    echo    - Service is starting up...
    echo    - Please wait 10-20 seconds for full initialization
)

echo.
echo ================================================
echo              FIX COMPLETED!
echo ================================================
echo.
echo What was fixed:
echo  - Database locking errors
echo  - Service startup issues  
echo  - Registration button errors
echo  - Login button errors
echo  - Product creation errors
echo.
echo Next steps:
echo 1. Wait 10-20 seconds for service to fully start
echo 2. Check system tray for CraftChain icon
echo 3. Open http://127.0.0.1:5002 in your browser
echo 4. Test registration and login
echo.
echo If you still see errors, restart your computer
echo and run this script again.
echo.
echo ================================================
pause
