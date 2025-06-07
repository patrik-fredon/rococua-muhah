# Makefile for FastAPI + Next.js Dashboard System
# Provides convenient commands for development and deployment

.PHONY: help install dev prod clean test lint format docker build deploy

# Default target
help:
	@echo "FastAPI + Next.js Dashboard System"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@echo "  help          Show this help message"
	@echo "  install       Install all dependencies"
	@echo "  dev           Start development servers"
	@echo "  prod          Start production servers"
	@echo "  clean         Clean up build artifacts and cache"
	@echo "  test          Run all tests"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code"
	@echo "  docker        Build and run with Docker Compose"
	@echo "  build         Build for production"
	@echo "  deploy        Deploy to production"
	@echo ""
	@echo "Environment Commands:"
	@echo "  setup-env     Setup environment files"
	@echo "  migrate       Run database migrations"
	@echo "  seed          Seed database with sample data"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build  Build Docker images"
	@echo "  docker-up     Start Docker services"
	@echo "  docker-down   Stop Docker services"
	@echo "  docker-logs   Show Docker logs"

# Installation
install:
	@echo "📦 Installing dependencies..."
	@cd app && pip install -r requirements.txt
	@cd dashboard && npm install
	@echo "✅ Dependencies installed successfully"

install-backend:
	@echo "📦 Installing backend dependencies..."
	@cd app && pip install -r requirements.txt
	@echo "✅ Backend dependencies installed"

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	@cd dashboard && npm install
	@echo "✅ Frontend dependencies installed"

# Development
dev:
	@echo "🚀 Starting development servers..."
	@python3 launcher.py --mode dev

dev-backend:
	@echo "🚀 Starting backend development server..."
	@cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "🚀 Starting frontend development server..."
	@cd dashboard && npm run dev

# Production
prod:
	@echo "🚀 Starting production servers..."
	@python3 launcher.py --mode prod

# Environment setup
setup-env:
	@echo "🔧 Setting up environment files..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example"; fi
	@if [ ! -f dashboard/.env.local ]; then cp dashboard/.env.example dashboard/.env.local; echo "Created dashboard/.env.local"; fi
	@echo "✅ Environment files ready"

# Database operations
migrate:
	@echo "🗄️ Running database migrations..."
	@alembic upgrade head
	@echo "✅ Migrations completed"

migrate-create:
	@echo "📝 Creating new migration..."
	@read -p "Enter migration message: " msg; alembic revision --autogenerate -m "$$msg"

seed:
	@echo "🌱 Seeding database..."
	@python3 -c "from app.scripts.seed_data import seed_database; seed_database()"
	@echo "✅ Database seeded"

# Testing
test:
	@echo "🧪 Running tests..."
	@cd app && python -m pytest tests/ -v
	@cd dashboard && npm run test
	@echo "✅ All tests passed"

test-backend:
	@echo "🧪 Running backend tests..."
	@cd app && python -m pytest tests/ -v

test-frontend:
	@echo "🧪 Running frontend tests..."
	@cd dashboard && npm run test

# Code quality
lint:
	@echo "🔍 Running linting checks..."
	@cd app && flake8 . --max-line-length=88 --exclude=migrations
	@cd dashboard && npm run lint
	@echo "✅ Linting passed"

format:
	@echo "🎨 Formatting code..."
	@cd app && black . --line-length=88 --exclude=migrations
	@cd app && isort . --profile black
	@cd dashboard && npm run format
	@echo "✅ Code formatted"

# Build
build:
	@echo "🏗️ Building for production..."
	@cd dashboard && npm run build
	@echo "✅ Build completed"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf app/__pycache__ app/**/__pycache__
	@rm -rf dashboard/.next dashboard/node_modules/.cache
	@rm -rf dashboard/out
	@find . -name "*.pyc" -delete
	@find . -name ".DS_Store" -delete
	@echo "✅ Cleanup completed"

# Docker operations
docker: docker-build docker-up

docker-build:
	@echo "🐳 Building Docker images..."
	@docker-compose build
	@echo "✅ Docker images built"

docker-up:
	@echo "🐳 Starting Docker services..."
	@docker-compose up -d
	@echo "✅ Docker services started"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Database: localhost:5432"

docker-down:
	@echo "🐳 Stopping Docker services..."
	@docker-compose down
	@echo "✅ Docker services stopped"

docker-logs:
	@echo "📋 Showing Docker logs..."
	@docker-compose logs -f

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Docker cleaned"

# Production deployment
deploy:
	@echo "🚀 Deploying to production..."
	@make build
	@make docker-build
	@echo "✅ Deployment ready"

# Health checks
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:8000/ || echo "❌ Backend not responding"
	@curl -f http://localhost:3000/ || echo "❌ Frontend not responding"

# Logs
logs-backend:
	@echo "📋 Backend logs..."
	@tail -f app/logs/app.log 2>/dev/null || echo "No log file found"

logs-frontend:
	@echo "📋 Frontend logs..."
	@cd dashboard && npm run logs 2>/dev/null || echo "No logs available"

# Development utilities
reset-db:
	@echo "🗄️ Resetting database..."
	@rm -f app.db
	@make migrate
	@make seed
	@echo "✅ Database reset"

update-deps:
	@echo "📦 Updating dependencies..."
	@cd app && pip install --upgrade -r requirements.txt
	@cd dashboard && npm update
	@echo "✅ Dependencies updated"

# Quick start
quick-start: setup-env install migrate dev

# Show project status
status:
	@echo "📊 Project Status"
	@echo "================"
	@echo "Backend URL: http://localhost:8000"
	@echo "Frontend URL: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Services:"
	@curl -s http://localhost:8000/ >/dev/null && echo "✅ Backend running" || echo "❌ Backend not running"
	@curl -s http://localhost:3000/ >/dev/null && echo "✅ Frontend running" || echo "❌ Frontend not running"
