# Check if Docker is running
$dockerInfo = docker info 2>&1
if ($LastExitCode -ne 0) {
    Write-Host "❌ Docker is not running or not installed." -ForegroundColor Red
    Write-Host "Please install Docker Desktop and start it."
    exit 1
}

Write-Host "🚀 Starting HomeControl Backend..." -ForegroundColor Green
docker-compose up --build
