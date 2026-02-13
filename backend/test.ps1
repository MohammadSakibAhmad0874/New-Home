Write-Host "🧪 Running Backend Tests..." -ForegroundColor Cyan

# Check/Install httpx
try {
    import-module httpx -ErrorAction Stop
} catch {
    Write-Host "Installing test dependencies (httpx)..."
    pip install httpx
}

# Run Test
python tests/test_flow.py
