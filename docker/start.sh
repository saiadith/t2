#!/bin/bash

# E-commerce Customer Analytics - Docker Startup Script

echo "🚀 Starting E-commerce Customer Analytics System..."
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "🎉 System is starting up!"
echo ""
echo "📈 Dashboard will be available at: http://localhost:8501"
echo "🔌 WebSocket server running on: ws://localhost:8765"
echo "🗄️  Database running on: localhost:5432"
echo ""
echo "📋 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop system: docker-compose down"
echo "  - Restart: docker-compose restart"
echo ""
echo "⏱️  Please wait 30-60 seconds for all services to fully initialize..." 