.PHONY: help dev stop clean health logs migrate test lint format build

# Default target
help:
	@echo "Commerce AI Core - Makefile Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start all services in development mode"
	@echo "  make stop         - Stop all services"
	@echo "  make clean        - Clean all temporary files and caches"
	@echo "  make logs         - View logs from all services"
	@echo ""
	@echo "Database:"
	@echo "  make migrate      - Run database migrations"
	@echo "  make reset-db     - Reset database (WARNING: destroys all data)"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-int     - Run integration tests only"
	@echo "  make test-e2e     - Run end-to-end tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make typecheck    - Run type checking"
	@echo ""
	@echo "Build:"
	@echo "  make build        - Build all services"
	@echo "  make build-web    - Build web frontend only"
	@echo "  make build-api    - Build API backend only"
	@echo ""
	@echo "Health:"
	@echo "  make health       - Check health of all services"

dev:
	@./scripts/dev.sh

stop:
	@./scripts/stop.sh

clean:
	@./scripts/clean.sh

logs:
	docker compose -f docker-compose.dev.yml logs -f

health:
	@./scripts/health.sh

migrate:
	@./scripts/migrate.sh

reset-db:
	@./scripts/reset-db.sh

test:
	@./scripts/test.sh

test-unit:
	@./scripts/test-unit.sh

test-int:
	@./scripts/test-integration.sh

test-e2e:
	@./scripts/test-e2e.sh

lint:
	@./scripts/lint.sh

format:
	@./scripts/format.sh

typecheck:
	@./scripts/typecheck.sh

build:
	@./scripts/build.sh

build-web:
	cd apps/web && pnpm build

build-api:
	docker build -f infra/docker/api.Dockerfile -t commerce-ai-core-api .
