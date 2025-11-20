# CraftChain Launcher - PowerShell version
# This script starts the Flask backend and opens the admin page

$ProjectDir = "C:\Users\darsh\OneDrive\Desktop\CRAFTCHAIN"
Set-Location $ProjectDir

# Use venv Python if available
$PythonExe = if (Test-Path ".venv\Scripts\python.exe") { 
    ".venv\Scripts\python.exe" 
} else { 
    "python" 
}

Write-Host "Starting CraftChain server..."
Write-Host "Project: $ProjectDir"
Write-Host "Python: $PythonExe"

# Start the Flask server in background
$ServerProcess = Start-Process -FilePath $PythonExe -ArgumentList "backend\app.py" -WorkingDirectory $ProjectDir -PassThru -WindowStyle Normal

# Wait for server to be ready (check both ports)
$MaxWait = 60
$ServerReady = $false
$ServerPort = $null

Write-Host "Waiting for server to start (up to $MaxWait seconds)..."

for ($i = 0; $i -lt $MaxWait; $i++) {
    Start-Sleep -Seconds 1
    
    # Check port 5002 first (default for backend\app.py)
    try {
        $Response = Invoke-WebRequest -Uri "http://127.0.0.1:5002/" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($Response.StatusCode -eq 200) {
            $ServerReady = $true
            $ServerPort = 5002
            break
        }
    } catch { }
    
    # Check port 5000 as fallback
    try {
        $Response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($Response.StatusCode -eq 200) {
            $ServerReady = $true
            $ServerPort = 5000
            break
        }
    } catch { }
    
    if ($i % 5 -eq 0) {
        Write-Host "Still waiting... ($i/$MaxWait)"
    }
}

if ($ServerReady) {
    Write-Host "Server ready on port $ServerPort! Opening admin page..."
    Start-Process "http://127.0.0.1:$ServerPort/admin"
} else {
    Write-Host "Server did not start within $MaxWait seconds."
    Write-Host "You can try manually: http://127.0.0.1:5002/admin"
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
