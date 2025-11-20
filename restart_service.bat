@echo off
echo Stopping CraftChain Service...

REM Kill any existing Python processes running the app
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul

REM Wait a moment for processes to terminate
timeout /t 5 /nobreak >nul

echo Fixing database issues...
python force_fix_database.py

echo Restarting CraftChain Service...
start "" powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\Users\darsh\OneDrive\Desktop\CRAFTCHAIN\CraftChain-Service.ps1"

echo Service restart initiated!
echo Check the system tray for the CraftChain icon.
pause
