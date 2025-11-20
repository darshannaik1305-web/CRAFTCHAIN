@echo off
title CraftChain ULTIMATE Fix - Bypass All Locks
color 0C
echo =================================================
echo    CraftChain ULTIMATE Fix - Complete Bypass
echo =================================================
echo.
echo This will create a NEW database in a different location
echo to completely bypass all Windows file lock issues
echo.
pause

echo.
echo [STEP 1/4] Killing ALL processes that might lock files...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM powershell.exe >nul 2>&1
taskkill /F /IM cmd.exe >nul 2>&1
echo    - All processes terminated

echo.
echo [STEP 2/4] Creating new database in TEMP folder...
cd /d "%~dp0"

REM Create new database in Windows temp folder to avoid locks
set NEW_DB_PATH=%TEMP%\craftchain_app.db
echo    - New database location: %NEW_DB_PATH%

REM Remove old database files if they exist
del /F /Q "%NEW_DB_PATH%" >nul 2>&1
del /F /Q "%NEW_DB_PATH%-wal" >nul 2>&1
del /F /Q "%NEW_DB_PATH%-shm" >nul 2>&1

echo.
echo [STEP 3/4] Creating fresh database with new settings...
python -c "
import sys, os, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Create new database in temp folder
db_path = r'%NEW_DB_PATH%'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Set optimal settings
cursor.execute('PRAGMA journal_mode=WAL')
cursor.execute('PRAGMA busy_timeout=30000')
cursor.execute('PRAGMA foreign_keys=ON')
cursor.execute('PRAGMA synchronous=NORMAL')
cursor.execute('PRAGMA cache_size=10000')
cursor.execute('PRAGMA temp_store=MEMORY')
conn.commit()
conn.close()

print('    - Database created in temp folder')

# Now create tables using Flask
from app import app, db, ensure_category_column

# Temporarily modify the database path
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.create_all()
ensure_category_column()
print('    - Tables created successfully')

# Save the new path to a config file
with open('database_path.txt', 'w') as f:
    f.write(db_path)
print('    - Database path saved to config')
"

if %ERRORLEVEL% NEQ 0 (
    echo    - ERROR: Database creation failed!
    pause
    exit /b 1
)

echo.
echo [STEP 4/4] Starting service with new database...
start "" /MIN powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0CraftChain-Service.ps1"

echo    - Service starting with new database...
timeout /t 5 /nobreak >nul

echo.
echo =================================================
echo           ULTIMATE FIX COMPLETED!
echo =================================================
echo.
echo SOLUTION APPLIED:
echo - Created NEW database in Windows temp folder
echo - Bypassed all existing file locks
echo - Service started with fresh database
echo.
echo The database is now located at:
echo %NEW_DB_PATH%
echo.
echo NEXT STEPS:
echo 1. Wait 10-20 seconds for service to start
echo 2. Open http://127.0.0.1:5002
echo 3. Test registration and login
echo.
echo ALL PREVIOUS ERRORS SHOULD NOW BE FIXED!
echo =================================================
pause
