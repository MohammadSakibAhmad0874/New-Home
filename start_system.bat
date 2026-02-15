@echo off
title SmartHome Control System - Launcher
color 0A

echo ========================================================
echo        SmartHome Control (Docker + Ngrok)
echo ========================================================
echo.

echo [1/3] Starting Backend Services (Docker)...
cd backend
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Docker failed to start. Is Docker Desktop running?
    pause
    exit
)
cd ..
echo [OK] Backend Started.

echo [2/3] Starting Ngrok Tunnel...
echo.
echo     IMPORTANT: Copy the URL from the new window!
echo.
start "Ngrok Tunnel" ngrok http 80

echo [3/3] Launching Dashboard...
echo.
echo Waiting 5 seconds for services to warm up...
timeout /t 5 /nobreak >nul

echo.
echo ========================================================
echo               SYSTEM IS READY
echo ========================================================
echo.
echo 1. Local Dashboard:  http://localhost/cloud/index.html
echo 2. Remote Dashboard: (Use the Ngrok URL opened in the other window)
echo.
echo Press any key to shutdown the system...
pause >nul

echo.
echo Stopping Services...
cd backend
docker-compose down
echo [OK] System Stopped.
pause
