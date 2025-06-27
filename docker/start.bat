@echo off
REM E-commerce Customer Analytics - Docker Startup Script for Windows

echo 🚀 Starting E-commerce Customer Analytics System...
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ docker-compose is not available. Please install Docker Compose.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are available

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up -d --build

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service status
echo 📊 Checking service status...
docker-compose ps

echo.
echo 🎉 System is starting up!
echo.
echo 📈 Dashboard will be available at: http://localhost:8501
echo 🔌 WebSocket server running on: ws://localhost:8765
echo 🗄️  Database running on: localhost:5432
echo.
echo 📋 Useful commands:
echo   - View logs: docker-compose logs -f
echo   - Stop system: docker-compose down
echo   - Restart: docker-compose restart
echo.
echo ⏱️  Please wait 30-60 seconds for all services to fully initialize...
pause 