.PHONY: help install dev test lint format migrate up down logs clean keys

# Default target
help:
	@echo "ATLAS - AI-Powered Recruitment Operating System"
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install all dependencies"
	@echo "  dev         - Start development environment"
	@echo "  test        - Run all tests"
	@echo "  lint        - Run linters and type checkers"
	@echo "  format      - Format code with ruff and black"
	@echo "  migrate     - Run database migrations"
	@echo "  up          - Start Docker services"
	@echo "  down        - Stop Docker services"
	@echo "  logs        - View Docker logs"
	@echo "  clean       - Clean build artifacts"
	@echo "  keys        - Generate JWT keys"

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -e ".[dev]"
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development environment
dev: keys up
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Generate JWT keys
keys:
	@./scripts/generate-keys.sh

# Start Docker services
up:
	docker-compose up -d

# Stop Docker services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm run test

# Run linters
lint:
	@echo "Running ruff..."
	cd backend && ruff check .
	@echo "Running mypy..."
	cd backend && mypy app/
	@echo "Running ESLint..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting with ruff..."
	cd backend && ruff format .
	@echo "Formatting with prettier..."
	cd frontend && npx prettier --write .

# Database migrations
migrate:
	cd backend && alembic upgrade head

# Create new migration
migrate-create:
	@read -p "Migration message: " msg; \
	cd backend && alembic revision --autogenerate -m "$$msg"

# Clean build artifacts
clean:
	@echo "Cleaning backend..."
	cd backend && rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
	@echo "Cleaning frontend..."
	cd frontend && rm -rf node_modules dist build .vite
	@echo "Cleaning Docker..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Run backend server
run-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend server
run-frontend:
	cd frontend && npm run dev

# Run Celery worker
run-worker:
	cd backend && celery -A app.infrastructure.celery worker --loglevel=info

# Run Celery beat
run-beat:
	cd backend && celery -A app.infrastructure.celery beat --loglevel=info

# Run Flower
run-flower:
	cd backend && celery -A app.infrastructure.celery flower --port=5555

# Database shell
db-shell:
	docker-compose exec postgres psql -U postgres -d atlas

# Redis shell
redis-shell:
	docker-compose exec redis redis-cli

# Backup database
backup-db:
	docker-compose exec postgres pg_dump -U postgres atlas > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Restore database
restore-db:
	@read -p "Backup file: " file; \
	docker-compose exec -T postgres psql -U postgres atlas < $$file