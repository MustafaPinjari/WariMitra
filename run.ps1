# WariMitra Full Stack Runner (Backend + Frontend)
# ===============================================
# Usage:
#   .\run.ps1                   (Opens Backend & Frontend in separate terminal windows)
#   .\run.ps1 -Mode Background  (Runs both as background jobs in the current window)
#   .\run.ps1 -OpenBrowser      (Launches browser automatically after starting)

param (
    [ValidateSet("NewWindow", "Background")]
    [string]$Mode = "NewWindow",

    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"
$rootDir = $PSScriptRoot

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   WariMitra Full Stack Launcher (Dev Mode)     " -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan

$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"

# 1. Validate directories
if (-not (Test-Path $backendDir)) {
    Write-Host "[ERROR] Backend directory not found at $backendDir" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendDir)) {
    Write-Host "[ERROR] Frontend directory not found at $frontendDir" -ForegroundColor Red
    exit 1
}

# 2. Check Python Environment for Backend
$pythonExec = Join-Path $backendDir "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExec)) {
    Write-Host "[WARNING] Virtual environment python executable not found at $pythonExec" -ForegroundColor Yellow
    Write-Host "Falling back to system python..." -ForegroundColor Yellow
    $pythonExec = "python"
}

# 3. Check for ADB & set up port forwarding for physical Android devices
if (Get-Command adb -ErrorAction SilentlyContinue) {
    $adbResult = & adb reverse tcp:8000 tcp:8000 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] ADB Reverse Port Forwarding enabled (http://127.0.0.1:8000 on physical device -> PC)" -ForegroundColor Cyan
    }
}

# 4. Launch Services
Write-Host "`n[+] Backend Path:  $backendDir" -ForegroundColor DarkGray
Write-Host "[+] Frontend Path: $frontendDir" -ForegroundColor DarkGray

if ($Mode -eq "NewWindow") {
    Write-Host "`n[+] Launching Backend (Django @ http://0.0.0.0:8000)..." -ForegroundColor Green
    $backendCmd = "Set-Location '$backendDir'; Write-Host '=== WARIMITRA BACKEND (Django) ===' -ForegroundColor Green; & '$pythonExec' manage.py runserver 0.0.0.0:8000"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

    Write-Host "[+] Launching Frontend (Next.js @ http://localhost:3000)..." -ForegroundColor Green
    $frontendCmd = "Set-Location '$frontendDir'; Write-Host '=== WARIMITRA FRONTEND (Next.js) ===' -ForegroundColor Cyan; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

    Write-Host "`n================================================" -ForegroundColor Cyan
    Write-Host " [SUCCESS] Backend & Frontend are running!" -ForegroundColor Green
    Write-Host "  - Frontend URL: http://localhost:3000/" -ForegroundColor White
    Write-Host "  - Backend API:  http://127.0.0.1:8000/api/ (Local) | http://<YOUR_PC_IP>:8000/api/ (Network/USB)" -ForegroundColor White
    Write-Host "  - Swagger Docs: http://127.0.0.1:8000/api/docs/" -ForegroundColor White
    Write-Host "================================================" -ForegroundColor Cyan
}
else {
    Write-Host "`n[+] Starting services as background jobs..." -ForegroundColor Yellow

    $backendJob = Start-Job -ScriptBlock {
        param($dir, $py)
        Set-Location $dir
        & $py manage.py runserver 0.0.0.0:8000
    } -ArgumentList $backendDir, $pythonExec

    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        npm run dev
    } -ArgumentList $frontendDir

    Write-Host "`n[SUCCESS] Background Jobs Started!" -ForegroundColor Green
    Write-Host "  Backend Job ID:  $($backendJob.Id)" -ForegroundColor Cyan
    Write-Host "  Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Cyan
    Write-Host "`nUseful Job Commands:" -ForegroundColor DarkGray
    Write-Host "  Get-Job                           (Check job status)" -ForegroundColor DarkGray
    Write-Host "  Receive-Job -Id $($backendJob.Id) -Keep    (View backend logs)" -ForegroundColor DarkGray
    Write-Host "  Receive-Job -Id $($frontendJob.Id) -Keep   (View frontend logs)" -ForegroundColor DarkGray
    Write-Host "  Stop-Job -Id $($backendJob.Id),$($frontendJob.Id)        (Stop both servers)" -ForegroundColor DarkGray
}

if ($OpenBrowser) {
    Write-Host "`n[+] Opening browser at http://localhost:3000..." -ForegroundColor Green
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:3000"
}
