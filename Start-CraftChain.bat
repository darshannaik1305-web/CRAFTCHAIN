@echo off
setlocal enableextensions

REM Resolve project directory (works even if this script runs from Startup folder)
set "PROJECT_DIR=%~dp0"
if not exist "%PROJECT_DIR%backend\app.py" (
  set "PROJECT_DIR=C:\Users\darsh\OneDrive\Desktop\CRAFTCHAIN\"
)
pushd "%PROJECT_DIR%"

REM Activate virtual environment if present
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)

REM Choose Python executable (prefer venv)
set "PYEXE=python"
if exist ".venv\Scripts\python.exe" set "PYEXE=.venv\Scripts\python.exe"

REM Start the Flask app (backend/app.py) in a new window; log output to server.log
set "LOGFILE=%~dp0server.log"
echo [%date% %time%] Starting server > "%LOGFILE%"
start "CRAFTCHAIN Server" cmd /c ""%PYEXE%" backend\app.py 1>>"%LOGFILE%" 2>&1"

REM Wait until the server is ready on 5002 or 5000 (up to ~60 seconds)
powershell -NoProfile -Command "\
$max=60; $ok=$false; $port=''; \
for($i=0;$i -lt $max;$i++){ \
  foreach($p in 5002,5000){ \
    try { $r=Invoke-WebRequest -UseBasicParsing ("http://127.0.0.1:$p/"); if($r.StatusCode -ge 200){ $ok=$true; $port=$p; break } } catch {} \
  } \
  if($ok){ break } \
  Start-Sleep -Milliseconds 1000 \
}; if($ok){ Write-Output $port } else { exit 1 }" > "%TEMP%\craftchain_port.txt"

set "PORT_CHOSEN="
for /f "usebackq delims=" %%p in ("%TEMP%\craftchain_port.txt") do set "PORT_CHOSEN=%%p"
del "%TEMP%\craftchain_port.txt" 2>nul

REM Open the admin page in the default browser if server responded
if defined PORT_CHOSEN (
  start "" http://127.0.0.1:%PORT_CHOSEN%/admin
) else (
  echo Server did not become ready in time. See log: "%LOGFILE%"
)

popd
endlocal
