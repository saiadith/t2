@echo off
REM E-commerce Customer Analytics - Docker Stop Script for Windows

echo 🛑 Stopping E-commerce Customer Analytics System...
echo ==================================================

REM Stop all services
echo ⏹️  Stopping services...
docker-compose down

echo.
echo ✅ All services have been stopped.
echo.
echo 📋 To start again, run: start.bat
echo 📋 To remove all data, run: docker-compose down -v
pause 