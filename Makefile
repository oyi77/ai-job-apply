# Makefile for AI Job Application Assistant
# Technical Debt Prevention and Code Quality

.PHONY: help install-hooks run-hooks check-quality check-debt fix-quality test coverage clean docker-up docker-down docker-build docker-logs docker-clean

# Default target
help:
	@echo "🔍 AI Job Application Assistant - Technical Debt Prevention"
	@echo "=========================================================="
	@echo ""
	@echo "📋 Available Commands:"
	@echo ""
	@echo "🔧 Setup & Installation:"
	@echo "  install-hooks    Install pre-commit hooks"
	@echo "  install-deps     Install development dependencies"
	@echo ""
	@echo "✅ Quality Checks:"
	@echo "  check-quality    Run all quality checks (format, lint, type-check)"
	@echo "  check-debt       Run technical debt analysis"
	@echo "  run-hooks        Run pre-commit hooks on all files"
	@echo ""
	@echo "🔧 Auto-fix:"
	@echo "  fix-quality      Auto-fix formatting and import issues"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test             Run all tests"
	@echo "  coverage         Run tests with coverage report"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean            Clean up generated files and caches"
	@echo "  update-deps      Update development dependencies"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  docker-up        Start all Docker containers (development)"
	@echo "  docker-down      Stop all Docker containers"
	@echo "  docker-build     Build Docker images"
	@echo "  docker-logs      View Docker container logs"
	@echo "  docker-clean     Remove containers, volumes, and images"
	@echo "  docker-prod      Start production environment"
	@echo ""
	@echo "📊 Reports:"
	@echo "  debt-report      Generate technical debt report"
	@echo "  quality-report   Generate code quality report"
	@echo ""

# Install pre-commit hooks
install-hooks:
	@echo "🔧 Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Pre-commit hooks installed successfully!"

# Install development dependencies
install-deps:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	pip install black isort flake8 mypy pytest pytest-cov pytest-asyncio
	pip install pre-commit bandit safety
	@echo "✅ Development dependencies installed!"

# Run pre-commit hooks on all files
run-hooks:
	@echo "🔍 Running pre-commit hooks on all files..."
	pre-commit run --all-files

# Check code quality
check-quality:
	@echo "🔍 Checking code quality..."
	@echo "📝 Formatting check..."
	black --check --diff .
	@echo "📚 Import sorting check..."
	isort --check-only --diff .
	@echo "🚨 Linting check..."
	flake8 --max-line-length=88 --extend-ignore=E203,W503,F401 src/ tests/
	@echo "🔒 Security check..."
	bandit -r src/ -f json -o bandit-report.json || true
	@echo "✅ Code quality checks completed!"

# Check technical debt
check-debt:
	@echo "🔍 Analyzing technical debt..."
	python scripts/technical-debt-monitor.py --project-root . --output technical-debt-report.json
	@echo "✅ Technical debt analysis completed!"

# Auto-fix quality issues
fix-quality:
	@echo "🔧 Auto-fixing quality issues..."
	@echo "📝 Formatting code..."
	black .
	@echo "📚 Sorting imports..."
	isort .
	@echo "🧹 Removing unused imports..."
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive src/ tests/
	@echo "✅ Quality issues auto-fixed!"

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

# Run tests with coverage
coverage:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=95

# Clean up generated files
clean:
	@echo "🧹 Cleaning up generated files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "bandit-report.json" -delete
	find . -type f -name "technical-debt-report.json" -delete
	@echo "✅ Cleanup completed!"

# Update development dependencies
update-deps:
	@echo "📦 Updating development dependencies..."
	pip install --upgrade black isort flake8 mypy pytest pytest-cov pytest-asyncio
	pip install --upgrade pre-commit bandit safety
	@echo "✅ Dependencies updated!"

# Generate technical debt report
debt-report:
	@echo "📊 Generating technical debt report..."
	python scripts/technical-debt-monitor.py --project-root . --output technical-debt-report.json
	@echo "✅ Report saved to technical-debt-report.json"

# Generate code quality report
quality-report:
	@echo "📊 Generating code quality report..."
	@echo "📝 Running Black..."
	black --check --diff . > quality-report.txt 2>&1 || true
	@echo "📚 Running isort..."
	isort --check-only --diff . >> quality-report.txt 2>&1 || true
	@echo "🚨 Running flake8..."
	flake8 --max-line-length=88 --extend-ignore=E203,W503,F401 src/ tests/ >> quality-report.txt 2>&1 || true
	@echo "🔒 Running bandit..."
	bandit -r src/ -f json -o bandit-report.json >> quality-report.txt 2>&1 || true
	@echo "✅ Quality report saved to quality-report.txt"

# Full quality check (used in CI/CD)
ci-check:
	@echo "🚀 Running CI/CD quality checks..."
	@make check-quality
	@make check-debt
	@make test
	@echo "✅ All CI/CD checks passed!"

# Pre-commit validation
validate-commit:
	@echo "🔍 Validating commit..."
	@make check-quality
	@make check-debt
	@echo "✅ Commit validation passed!"

# Daily development workflow
dev-workflow:
	@echo "🔄 Running daily development workflow..."
	@make fix-quality
	@make check-quality
	@make test
	@make check-debt
	@echo "✅ Daily workflow completed!"

# Weekly debt review
weekly-review:
	@echo "📅 Running weekly technical debt review..."
	@make check-debt
	@make quality-report
	@echo "📊 Reports generated for weekly review"
	@echo "📁 Check technical-debt-report.json and quality-report.txt"

# Emergency debt cleanup
emergency-cleanup:
	@echo "🚨 Emergency technical debt cleanup..."
	@echo "⚠️  This will attempt to fix all quality issues automatically"
	@make fix-quality
	@make check-quality
	@make check-debt
	@echo "✅ Emergency cleanup completed!"

# Show current debt status
debt-status:
	@echo "📊 Current technical debt status..."
	python scripts/technical-debt-monitor.py --project-root . --quiet --output /tmp/debt-status.json
	@echo "📁 Full report saved to /tmp/debt-status.json"

# Install all tools and run initial check
setup:
	@echo "🚀 Setting up development environment..."
	@make install-deps
	@make install-hooks
	@make check-debt
	@echo "✅ Development environment setup completed!"
	@echo "🎯 You can now use: make dev-workflow"

# Show help for specific command
help-%:
	@echo "Help for command: $*"
	@echo "Run 'make $*' to execute this command"

# Docker Commands
docker-up:
	@echo "🐳 Starting Docker containers (development)..."
	docker-compose up -d
	@echo "✅ Containers started! Frontend: http://localhost:5173, Backend: http://localhost:8000"

docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down
	@echo "✅ Containers stopped!"

docker-build:
	@echo "🔨 Building Docker images..."
	docker-compose build
	@echo "✅ Images built!"

docker-logs:
	@echo "📋 Viewing Docker logs (Ctrl+C to exit)..."
	docker-compose logs -f

docker-clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Docker cleanup completed!"

docker-prod:
	@echo "🏭 Starting production environment..."
	@if [ ! -f .env.prod ]; then \
		echo "⚠️  Warning: .env.prod not found. Using .env"; \
		docker-compose -f docker-compose.prod.yml up -d --build; \
	else \
		docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build; \
	fi
	@echo "✅ Production environment started!"

docker-restart:
	@echo "🔄 Restarting Docker containers..."
	docker-compose restart
	@echo "✅ Containers restarted!"

docker-ps:
	@echo "📊 Docker container status:"
	docker-compose ps

docker-shell-backend:
	@echo "🐚 Opening backend shell..."
	docker-compose exec backend bash

docker-shell-frontend:
	@echo "🐚 Opening frontend shell..."
	docker-compose exec frontend sh

docker-shell-db:
	@echo "🐚 Opening database shell..."
	docker-compose exec postgres psql -U postgres -d ai_job_assistant
