#!/bin/bash

# Technical Debt Prevention Setup Script
# AI Job Application Assistant

set -e

echo "🚀 Setting up Technical Debt Prevention for AI Job Application Assistant"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.9" | bc -l) -eq 1 ]]; then
    print_success "Python $python_version detected (>= 3.9 required)"
else
    print_error "Python 3.9+ required, found $python_version"
    exit 1
fi

print_status "Installing Python development dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install black isort flake8 mypy pytest pytest-cov pytest-asyncio
pip install pre-commit bandit safety autoflake

print_success "Python dependencies installed"

print_status "Installing pre-commit hooks..."
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg

print_success "Pre-commit hooks installed"

print_status "Installing Node.js dependencies for frontend..."
if [ -d "frontend" ]; then
    cd frontend
    npm ci
    cd ..
    print_success "Frontend dependencies installed"
else
    print_warning "Frontend directory not found, skipping frontend setup"
fi

print_status "Creating .pre-commit-config.yaml if it doesn't exist..."
if [ ! -f ".pre-commit-config.yaml" ]; then
    cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.9
        args: [--line-length=88, --target-version=py39]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black, --line-length=88]
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503,F401]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict, --ignore-missing-imports]
  
  - repo: https://github.com/pycqa/autoflake
    rev: v2.2.1
    hooks:
      - id: autoflake
        args: [--in-place, --remove-all-unused-imports, --remove-unused-variables]
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, src/, -f, json, -o, bandit-report.json]
        exclude: tests/
  
  - repo: https://github.com/PyCQA/safety
    rev: 3.0.1
    hooks:
      - id: safety
        args: [--full-report]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
      - id: check-case-conflict
      - id: check-docstring-first
      - id: check-symlinks
      - id: debug-statements
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: requirements-txt-fixer
      - id: check-todo
        args: [--max-issues=0]
EOF
    print_success ".pre-commit-config.yaml created"
else
    print_status ".pre-commit-config.yaml already exists"
fi

print_status "Creating Makefile if it doesn't exist..."
if [ ! -f "Makefile" ]; then
    cat > Makefile << 'EOF'
# Makefile for AI Job Application Assistant
# Technical Debt Prevention and Code Quality

.PHONY: help install-hooks run-hooks check-quality check-debt fix-quality test coverage clean

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
EOF
    print_success "Makefile created"
else
    print_status "Makefile already exists"
fi

print_status "Creating .vscode/settings.json for IDE configuration..."
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.args": ["--profile", "black"],
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.suggest.autoImports": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "python.linting.mypyEnabled": true,
  "python.linting.mypyArgs": [
    "--strict",
    "--ignore-missing-imports"
  ],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/htmlcov": true,
    "**/.coverage": true
  }
}
EOF
print_success "VS Code configuration created"

print_status "Running initial technical debt analysis..."
if [ -f "scripts/technical-debt-monitor.py" ]; then
    python scripts/technical-debt-monitor.py --project-root . --output initial-debt-report.json
    print_success "Initial technical debt analysis completed"
    print_status "Check initial-debt-report.json for results"
else
    print_warning "Technical debt monitor script not found, skipping initial analysis"
fi

print_status "Running pre-commit hooks on all files..."
pre-commit run --all-files || print_warning "Some pre-commit hooks failed (this is normal for initial setup)"

echo ""
echo "🎉 Technical Debt Prevention Setup Complete!"
echo "==========================================="
echo ""
echo "📋 What was installed:"
echo "  ✅ Python development tools (black, isort, flake8, mypy, pytest)"
echo "  ✅ Security tools (bandit, safety)"
echo "  ✅ Pre-commit hooks"
echo "  ✅ Makefile with quality commands"
echo "  ✅ VS Code configuration"
echo "  ✅ Pre-commit configuration"
echo ""
echo "🚀 Quick Start Commands:"
echo "  make help              - Show all available commands"
echo "  make check-quality     - Run all quality checks"
echo "  make check-debt        - Analyze technical debt"
echo "  make fix-quality       - Auto-fix formatting issues"
echo "  make dev-workflow      - Run daily development workflow"
echo ""
echo "🔧 Pre-commit hooks are now active!"
echo "   Every commit will automatically run quality checks"
echo ""
echo "📊 Next Steps:"
echo "  1. Review initial-debt-report.json for current debt status"
echo "  2. Run 'make check-quality' to see current quality status"
echo "  3. Use 'make fix-quality' to auto-fix common issues"
echo "  4. Set up weekly debt review with your team"
echo ""
echo "🎯 Remember: Technical debt is a choice, not a necessity!"
echo "   Every line of code should improve the system, not burden it."
echo ""
print_success "Setup completed successfully!"
