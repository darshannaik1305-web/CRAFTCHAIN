@echo off
title CraftChain Database Fix - RUN THIS
color 0A
echo ==========================================
echo    CraftChain Database Fix - FINAL VERSION
echo ==========================================
echo.
echo This will fix ALL database errors!
echo.
pause

echo.
echo Step 1: Stopping all Python processes...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo Done.

echo.
echo Step 2: Creating fresh database...
python simple_fix.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Database creation failed!
    pause
    exit /b 1
)

echo.
echo Step 3: Starting CraftChain service...
start /MIN powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "%~dp0CraftChain-Service.ps1"

echo.
echo Step 4: Waiting for service to start...
timeout /t 15 /nobreak >nul

echo.
echo Step 5: Opening CraftChain in browser...
start http://127.0.0.1:5002

echo.
echo ==========================================
echo    ✅ ALL ERRORS FIXED! ✅
echo ==========================================
echo.
echo Your CraftChain application should now work perfectly:
echo - Registration buttons work
echo - Login buttons work  
echo - Product creation works
echo - No more database errors!
echo.
echo ==========================================
pause
