$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== Automated Setup: AGY Thesis Starter Kit (PKN STAN) ===" -ForegroundColor Cyan

$PyCmd = $null
$PyArgs = @()
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PyCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PyCmd = "py"
    $PyArgs = @("-3")
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PyCmd = "python3"
} else {
    Write-Host "[ERROR] Python is not installed or not in PATH. Install Python 3.10+ from python.org and check 'Add Python to PATH'." -ForegroundColor Red
    exit 1
}

Write-Host "1. Installing required Python packages from requirements.txt..." -ForegroundColor Yellow
& $PyCmd @PyArgs -m pip install --upgrade pip
& $PyCmd @PyArgs -m pip install -r "$Root\requirements.txt"

if (-not (Test-Path "$Root\thesis_config.json")) {
    Copy-Item "$Root\thesis_config.example.json" "$Root\thesis_config.json"
    Write-Host "2. Created starter thesis_config.json from template." -ForegroundColor Green
} else {
    Write-Host "2. thesis_config.json already exists (skipped)." -ForegroundColor DarkGray
}

Write-Host "3. Running final readiness verification..." -ForegroundColor Yellow
& $PyCmd @PyArgs "$Root\scripts\setup_check.py"
