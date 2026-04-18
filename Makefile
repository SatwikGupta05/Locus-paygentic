.PHONY: help install dev build up down logs clean test lint format register

# Default target
help:
	@echo "AURORA-AI Trading Agents - Makefile"
	@echo "===================================="
	@echo ""
	@echo "Installation & Setup:"
	@echo "  make install        - Install Python and Node.js dependencies"
	@echo "  make register       - Register agent on ERC-8004 and claim capital"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start local development (API + Frontend)"
	@echo "  make dev-api        - Start API server only (port 8000)"
	@echo "  make dev-frontend   - Start Next.js frontend only (port 3000)"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Lint Python code"
	@echo "  make format         - Format Python code"
	@echo ""
	@echo "Docker & Deployment:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start services with Docker Compose"
	@echo "  make down           - Stop all Docker services"
	@echo "  make logs           - Tail logs from all services"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove .env (CAREFUL!), logs, __pycache__"
	@echo "  make docker-clean   - Remove all Docker images and volumes"
	@echo ""

# ─── Installation ────────────────────────────────────────────────────────

install:
	@echo "Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	cd frontend && npm install
	@echo "✅ Dependencies installed"

install-python:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Python dependencies installed"

install-frontend:
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed"

# ─── Registration & Blockchain Setup ────────────────────────────────────

register:
	@echo "Registering AURORA Agent on ERC-8004..."
	python scripts/register_agent.py

register-dry-run:
	@echo "Running registration in DRY-RUN mode..."
	python scripts/register_agent.py --dry-run

register-no-claim:
	@echo "Registering AURORA Agent (without claiming vault)..."
	python scripts/register_agent.py --no-claim

# ─── Development ────────────────────────────────────────────────────────

dev: dev-api dev-frontend
	@echo "🚀 Development environment started!"
	@echo "API: http://localhost:8000"
	@echo "Dashboard: http://localhost:3000"

dev-api:
	@echo "Starting API server (port 8000)..."
	python -m backend.main

dev-frontend:
	@echo "Starting Next.js frontend (port 3000)..."
	cd frontend && npm run dev

# ─── Testing & Linting ──────────────────────────────────────────────────

test:
	@echo "Running tests..."
	pytest backend/ -v --tb=short

test-coverage:
	@echo "Running tests with coverage..."
	pytest backend/ --cov=backend --cov-report=html --cov-report=term

lint:
	@echo "Linting Python code..."
	pylint backend/ --disable=C,R --fail-under=7.0 || true

format:
	@echo "Formatting Python code..."
	black backend/ scripts/
	isort backend/ scripts/
	@echo "✅ Code formatted"

# ─── Docker & Deployment ────────────────────────────────────────────────

build:
	@echo "Building Docker images..."
	docker-compose build --no-cache

build-api:
	@echo "Building API container..."
	docker build -t aurora-ai-api:latest .

build-frontend:
	@echo "Building Frontend container..."
	docker build -t aurora-ai-frontend:latest ./frontend

up:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d
	@echo "✅ Services started"
	@echo "API: http://localhost:8000"
	@echo "Dashboard: http://localhost:3000"

up-dev:
	@echo "Starting services in dev mode (logs attached)..."
	docker-compose up

down:
	@echo "Stopping all services..."
	docker-compose down

ps:
	@echo "Running containers:"
	docker-compose ps

logs:
	@echo "Tailing logs from all services..."
	docker-compose logs -f

logs-api:
	@echo "Tailing logs from API..."
	docker-compose logs -f api

logs-frontend:
	@echo "Tailing logs from Frontend..."
	docker-compose logs -f frontend

shell-api:
	@echo "Entering API container shell..."
	docker-compose exec api /bin/bash

shell-frontend:
	@echo "Entering Frontend container shell..."
	docker-compose exec frontend /bin/sh

# ─── Database & Migrations ──────────────────────────────────────────────

db-migrate:
	@echo "Running database migrations..."
	python -c "from backend.database.db_manager import DBManager; from backend.utils.config import MIGRATIONS_DIR, get_settings; db = DBManager(get_settings().db_path, MIGRATIONS_DIR); db.run_migrations()"
	@echo "✅ Migrations completed"

db-reset:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] && rm -f backend/state/trading.db && $(MAKE) db-migrate

# ─── Cleanup ─────────────────────────────────────────────────────────────

clean:
	@echo "Cleaning up..."
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete
	find frontend -type d -name node_modules -prune -o -type f -name "*.log" -delete
	rm -rf .pytest_cache build dist *.egg-info
	@echo "✅ Cleanup completed"

clean-logs:
	@echo "Clearing logs..."
	rm -rf backend/logs/*
	@echo "✅ Logs cleared"

docker-clean:
	@echo "⚠️  WARNING: This will remove all AURORA Docker images and volumes!"
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] && docker-compose down -v && docker rmi aurora-ai-api aurora-ai-frontend

# ─── Health & Status ────────────────────────────────────────────────────

health:
	@echo "Checking service health..."
	@curl -s -X GET http://localhost:8000/health | json_pp || echo "API not responding"

status:
	@echo "=== AURORA AI Trading Agent Status ==="
	@echo ""
	@echo "Docker Containers:"
	@docker-compose ps
	@echo ""
	@echo "Health Check:"
	@curl -s -X GET http://localhost:8000/health | json_pp || echo "⚠️  API not responding"

# ─── Quick Start ─────────────────────────────────────────────────────────

quickstart: install db-migrate register up
	@echo "🎉 AURORA AI is ready to trade!"

# ─── Documentation ──────────────────────────────────────────────────────

docs-api:
	@echo "API Documentation available at: http://localhost:8000/docs"

# ─── Environment ────────────────────────────────────────────────────────

env-example:
	@echo "Copying .env.example to .env..."
	cp .env.example .env
	@echo "✅ .env created (update with your credentials)"

env-show:
	@echo "=== Non-sensitive configuration ==="
	@grep -E "ENV|MODE|SYMBOL|TIMEFRAME|PORT|EXECUTION" .env || echo "No .env found"

# ─── Version & Info ─────────────────────────────────────────────────────

version:
	@echo "AURORA AI Trading Agents"
	@echo "Version: 1.0.0-hackathon"
	@python --version
	@node --version
	@docker --version

info:
	@echo "=== AURORA AI Project Info ==="
	@echo "Project: AURORA-AI Trading Agents"
	@echo "Purpose: ERC-8004 Trustless AI Trading with Kraken"
	@echo "Hackathon: AI Trading Agents (Mar 30 - Apr 12, 2026)"
	@echo ""
	@echo "Backend: Python (FastAPI, Web3, CCXT)"
	@echo "Frontend: Next.js + React + TailwindCSS"
	@echo "Blockchain: Sepolia (ERC-8004)"
	@echo "DEX: Kraken (via CLI/API)"
	@echo ""
	@echo "For more info, see README.md"
