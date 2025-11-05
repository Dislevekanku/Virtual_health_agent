# Virtual Health Assistant - Frontend Startup Script

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Virtual Health Assistant - Frontend Server" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if key.json exists
if (-not (Test-Path "key.json")) {
    Write-Host "[ERROR] key.json not found!" -ForegroundColor Red
    Write-Host "Please ensure key.json is in the current directory." -ForegroundColor Yellow
    exit 1
}

# Check if agent_info.json exists
if (-not (Test-Path "agent_info.json")) {
    Write-Host "[ERROR] agent_info.json not found!" -ForegroundColor Red
    Write-Host "Please ensure agent_info.json is in the current directory." -ForegroundColor Yellow
    exit 1
}

# Check if Flask is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    $flaskVersion = python -c "import flask; print('OK')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Flask not installed. Installing dependencies..." -ForegroundColor Red
        pip install -r requirements.txt
    } else {
        Write-Host "[OK] Flask is installed" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not check Flask. Attempting to install..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host ""
Write-Host "Frontend will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Flask server
python app.py

