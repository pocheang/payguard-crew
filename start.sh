#!/bin/bash

# PayGuard Quick Start Script
# This script helps you quickly deploy PayGuard using Docker

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           PayGuard Docker Quick Start                        ║"
echo "║  Enterprise Payment Risk Control & Compliance Audit System   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"
echo "✅ Docker Compose found: $(docker-compose --version)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Please edit .env file and update the following:"
    echo "   - JWT_SECRET_KEY"
    echo "   - POSTGRES_PASSWORD"
    echo "   - REDIS_PASSWORD"
    echo "   - API_KEY_ADMIN"
    echo "   - OPENAI_API_KEY (if using LLM features)"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Ask deployment mode
echo "Choose deployment mode:"
echo "1) Development (with hot-reload, SQLite)"
echo "2) Production (PostgreSQL, Redis, optimized)"
echo ""
read -p "Enter your choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting in DEVELOPMENT mode..."
        docker-compose -f docker-compose.dev.yml up -d
        ;;
    2)
        echo ""
        echo "🚀 Starting in PRODUCTION mode..."
        docker-compose up -d --build
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health..."

if curl -f http://localhost:8000/api/health/health > /dev/null 2>&1; then
    echo "✅ Backend API is healthy"
else
    echo "⚠️  Backend API is not responding yet (may need more time)"
fi

if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "⚠️  Frontend is not responding yet (may need more time)"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 🎉 PayGuard is Starting!                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Access Points:"
echo "   Frontend:     http://localhost"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "🔑 Test Accounts:"
echo "   Admin:    admin / admin123"
echo "   Analyst:  demo / demo123"
echo ""
echo "📊 Useful Commands:"
echo "   View logs:          docker-compose logs -f"
echo "   Stop services:      docker-compose down"
echo "   Restart service:    docker-compose restart <service>"
echo "   View status:        docker-compose ps"
echo ""
echo "📚 Documentation:"
echo "   Quick Start:  cat DOCKER.md"
echo "   Frontend:     cat frontend/QUICKSTART.md"
echo ""
echo "Happy auditing! 🛡️"
