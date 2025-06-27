#!/bin/bash

# E-commerce Customer Analytics - Docker Stop Script

echo "🛑 Stopping E-commerce Customer Analytics System..."
echo "=================================================="

# Stop all services
echo "⏹️  Stopping services..."
docker-compose down

echo ""
echo "✅ All services have been stopped."
echo ""
echo "📋 To start again, run: ./start.sh"
echo "📋 To remove all data, run: docker-compose down -v" 