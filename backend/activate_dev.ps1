# WariMitra Backend Helper
# ========================
# Run this first: . .\activate_dev.ps1
# After that you can just use: python manage.py <command>

$venvPath = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"

if (Test-Path $venvPath) {
    & $venvPath
    Write-Host ""
    Write-Host "  [OK] WariMitra venv activated!" -ForegroundColor Green
    Write-Host "  Python: $(python --version)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Useful commands:" -ForegroundColor Yellow
    Write-Host "    python manage.py runserver       -- Start Django dev server"
    Write-Host "    python manage.py seed_demo_data  -- Seed all demo data"
    Write-Host "    python manage.py migrate         -- Run database migrations"
    Write-Host "    python manage.py createsuperuser -- Create admin user"
    Write-Host "    python manage.py shell           -- Django interactive shell"
    Write-Host ""
} else {
    Write-Host "  [ERROR] venv not found at: $venvPath" -ForegroundColor Red
    Write-Host "  Run: python -m venv venv" -ForegroundColor Yellow
}
