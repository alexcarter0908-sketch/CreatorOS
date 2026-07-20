Write-Host "Checking for conflicting Docker backend container..." -ForegroundColor Cyan

$dockerBackend = docker ps --filter "name=creatoros-main-backend-1" --format "{{.Names}}"

if ($dockerBackend) {
    Write-Host "Found running Docker backend ($dockerBackend) - stopping it to avoid port 8000 conflicts..." -ForegroundColor Yellow
    docker stop creatoros-main-backend-1 | Out-Null
    Write-Host "Docker backend stopped." -ForegroundColor Green
} else {
    Write-Host "No conflicting Docker backend running - good." -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting local uvicorn (backend)..." -ForegroundColor Cyan
Set-Location "C:\Users\hp\Downloads\CreatorOS\CreatorOS-main\backend"
uvicorn app.main:app --reload
