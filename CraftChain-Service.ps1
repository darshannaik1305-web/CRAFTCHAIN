# CraftChain Persistent Service - PowerShell version
# This script runs the Flask backend as a persistent background service with system tray icon

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$ProjectDir = "C:\Users\darsh\OneDrive\Desktop\CRAFTCHAIN"
$LogFile = Join-Path $ProjectDir "service.log"
$PidFile = Join-Path $ProjectDir "server.pid"

# Use venv Python if available
$PythonExe = if (Test-Path (Join-Path $ProjectDir ".venv\Scripts\python.exe")) { 
    Join-Path $ProjectDir ".venv\Scripts\python.exe"
} else { 
    "python" 
}

# Global variables
$Global:ServerProcess = $null
$Global:NotifyIcon = $null
$Global:ContextMenu = $null
$Global:Timer = $null

function Write-Log {
    param($Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
}

function Test-ServerRunning {
    try {
        $Response = Invoke-WebRequest -Uri "http://127.0.0.1:5002/" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        return $Response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-Server {
    if ($Global:ServerProcess -and !$Global:ServerProcess.HasExited) {
        Write-Log "Server already running (PID: $($Global:ServerProcess.Id))"
        return
    }

    Write-Log "Starting CraftChain server..."
    try {
        $Global:ServerProcess = Start-Process -FilePath $PythonExe -ArgumentList "backend\app.py" -WorkingDirectory $ProjectDir -PassThru -WindowStyle Hidden -RedirectStandardOutput (Join-Path $ProjectDir "server_output.log") -RedirectStandardError (Join-Path $ProjectDir "server_error.log")
        
        if ($Global:ServerProcess) {
            Write-Log "Server started with PID: $($Global:ServerProcess.Id)"
            $Global:ServerProcess.Id | Out-File -FilePath $PidFile -Force
            
            # Wait a moment for server to initialize
            Start-Sleep -Seconds 3
            
            if (Test-ServerRunning) {
                Write-Log "Server is responding on http://127.0.0.1:5002"
                Update-TrayIcon -Status "Running" -Color "Green"
            } else {
                Write-Log "Server started but not responding yet"
                Update-TrayIcon -Status "Starting" -Color "Yellow"
            }
        }
    } catch {
        Write-Log "Failed to start server: $($_.Exception.Message)"
        Update-TrayIcon -Status "Error" -Color "Red"
    }
}

function Stop-Server {
    Write-Log "Stopping server..."
    if ($Global:ServerProcess -and !$Global:ServerProcess.HasExited) {
        try {
            $Global:ServerProcess.Kill()
            $Global:ServerProcess.WaitForExit(5000)
            Write-Log "Server stopped"
        } catch {
            Write-Log "Error stopping server: $($_.Exception.Message)"
        }
    }
    
    # Clean up PID file
    if (Test-Path $PidFile) {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
    
    Update-TrayIcon -Status "Stopped" -Color "Gray"
}

function Update-TrayIcon {
    param($Status, $Color)
    
    if ($Global:NotifyIcon) {
        $Global:NotifyIcon.Text = "CraftChain Server - $Status"
        
        # Create a simple colored icon (16x16 bitmap)
        $Bitmap = New-Object System.Drawing.Bitmap(16, 16)
        $Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
        
        $ColorBrush = switch ($Color) {
            "Green" { [System.Drawing.Brushes]::Green }
            "Yellow" { [System.Drawing.Brushes]::Orange }
            "Red" { [System.Drawing.Brushes]::Red }
            default { [System.Drawing.Brushes]::Gray }
        }
        
        $Graphics.FillEllipse($ColorBrush, 2, 2, 12, 12)
        $Graphics.Dispose()
        
        $Global:NotifyIcon.Icon = [System.Drawing.Icon]::FromHandle($Bitmap.GetHicon())
    }
}

function Create-TrayIcon {
    # Create context menu
    $Global:ContextMenu = New-Object System.Windows.Forms.ContextMenuStrip
    
    $StartItem = New-Object System.Windows.Forms.ToolStripMenuItem("Start Server")
    $StartItem.add_Click({ Start-Server })
    
    $StopItem = New-Object System.Windows.Forms.ToolStripMenuItem("Stop Server")
    $StopItem.add_Click({ Stop-Server })
    
    $RestartItem = New-Object System.Windows.Forms.ToolStripMenuItem("Restart Server")
    $RestartItem.add_Click({ Stop-Server; Start-Sleep 2; Start-Server })
    
    $OpenAdminItem = New-Object System.Windows.Forms.ToolStripMenuItem("Open Admin Panel")
    $OpenAdminItem.add_Click({ Start-Process "http://127.0.0.1:5002/admin" })
    
    $OpenHomeItem = New-Object System.Windows.Forms.ToolStripMenuItem("Open Website")
    $OpenHomeItem.add_Click({ Start-Process "http://127.0.0.1:5002/" })
    
    $SeparatorItem = New-Object System.Windows.Forms.ToolStripSeparator
    
    $ExitItem = New-Object System.Windows.Forms.ToolStripMenuItem("Exit")
    $ExitItem.add_Click({ 
        Stop-Server
        $Global:NotifyIcon.Dispose()
        [System.Windows.Forms.Application]::Exit()
    })
    
    $Global:ContextMenu.Items.AddRange(@($StartItem, $StopItem, $RestartItem, $SeparatorItem, $OpenAdminItem, $OpenHomeItem, $SeparatorItem, $ExitItem))
    
    # Create notify icon
    $Global:NotifyIcon = New-Object System.Windows.Forms.NotifyIcon
    $Global:NotifyIcon.ContextMenuStrip = $Global:ContextMenu
    $Global:NotifyIcon.Visible = $true
    
    # Double-click to open admin panel
    $Global:NotifyIcon.add_DoubleClick({ Start-Process "http://127.0.0.1:5002/admin" })
    
    Update-TrayIcon -Status "Starting" -Color "Yellow"
}

function Monitor-Server {
    if ($Global:ServerProcess -and $Global:ServerProcess.HasExited) {
        Write-Log "Server process exited unexpectedly. Restarting..."
        Start-Server
    } elseif ($Global:ServerProcess -and !$Global:ServerProcess.HasExited) {
        # Check if server is still responding
        if (!(Test-ServerRunning)) {
            Write-Log "Server not responding. Restarting..."
            Stop-Server
            Start-Sleep 2
            Start-Server
        } else {
            Update-TrayIcon -Status "Running" -Color "Green"
        }
    }
}

# Main execution
Write-Log "CraftChain Service starting..."

# Clean up any existing PID file
if (Test-Path $PidFile) {
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

# Create system tray icon
Create-TrayIcon

# Start the server
Start-Server

# Create timer for monitoring (check every 30 seconds)
$Global:Timer = New-Object System.Windows.Forms.Timer
$Global:Timer.Interval = 30000  # 30 seconds
$Global:Timer.add_Tick({ Monitor-Server })
$Global:Timer.Start()

Write-Log "Service started. Right-click system tray icon for options."

# Show initial notification
$Global:NotifyIcon.ShowBalloonTip(3000, "CraftChain Service", "Server is starting up...", [System.Windows.Forms.ToolTipIcon]::Info)

# Keep the script running
try {
    [System.Windows.Forms.Application]::Run()
} finally {
    # Cleanup on exit
    if ($Global:Timer) { $Global:Timer.Dispose() }
    if ($Global:NotifyIcon) { $Global:NotifyIcon.Dispose() }
    Stop-Server
    Write-Log "Service stopped."
}
