$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "====================================="
Write-Host "        ComicCraft Launcher"
Write-Host "====================================="
Write-Host ""

if (!(Test-Path ".venv")) {

    Write-Host "Creating virtual environment..."

    py -3 -m venv .venv
}

Write-Host "Activating virtual environment..."

& ".\.venv\Scripts\Activate.ps1"

Write-Host "Installing dependencies..."

python -m pip install --upgrade pip

pip install -r requirements.txt

Write-Host ""
Write-Host "Starting ComicCraft..."
Write-Host ""

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000