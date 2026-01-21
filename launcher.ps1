Write-Host "Glitcher - Professional Web Security Testing Platform" -ForegroundColor Green
Write-Host ""
Write-Host "Choose an option:" -ForegroundColor Yellow
Write-Host "1. Web Version (Node.js)" -ForegroundColor White
Write-Host "2. GUI Version (Python)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1 or 2)"

switch ($choice) {
    "1" {
        Write-Host "Starting Glitcher Web Version..." -ForegroundColor Cyan
        npm start
    }
    "2" {
        Write-Host "Starting Glitcher Python GUI Version..." -ForegroundColor Cyan
        python run_glitcher.py
    }
    default {
        Write-Host "Invalid choice. Please run the script again and select 1 or 2." -ForegroundColor Red
    }
}

Read-Host "Press Enter to continue"