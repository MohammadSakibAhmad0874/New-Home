Write-Host "🧪 Running WebSocket Tests..." -ForegroundColor Cyan

# Check/Install websockets and httpx
try {
    import-module websockets -ErrorAction Stop
}
catch {
    Write-Host "Installing test dependencies (websockets)..."
    pip install websockets
}

$baseUrl = "http://localhost/api/v1"

try {
    import-module httpx -ErrorAction Stop
}
catch {
    Write-Host "Installing test dependencies (httpx)..."
    pip install httpx
}

# Run Test
python tests/test_websocket.py
