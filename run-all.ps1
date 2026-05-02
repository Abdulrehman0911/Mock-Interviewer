# Run both backend and frontend in separate windows (development only)
# Usage: Open PowerShell in the mock-interviewer folder and run: .\run-all.ps1

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $repoRoot "backend"
$frontendPath = Join-Path $repoRoot "frontend"
$pythonExe = "d:/Projects/AI_Project/.venv/Scripts/python.exe"

Write-Host "Starting backend..."
Start-Process -FilePath $pythonExe -ArgumentList "$backendPath\app.py" -WorkingDirectory $backendPath

Start-Sleep -Seconds 2
Write-Host "Starting frontend (npm run dev)..."
Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory $frontendPath

Write-Host "Both processes started. Check the new windows for logs."