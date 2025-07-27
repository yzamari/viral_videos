# Makefile for ViralAI project
# Provides simple commands for common tasks

.PHONY: test test-quick test-full test-release install clean lint format help

# Default target
help:
	@echo "ViralAI Development Commands:"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run sanity tests (quick)"
	@echo "  make test-quick    - Run sanity tests (alias)"
	@echo "  make test-full     - Run full test suite with coverage"
	@echo "  make test-release  - Run release candidate tests"
	@echo "  make test-integration - Run integration tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run code linting"
	@echo "  make format        - Format code with black"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install dependencies"
	@echo "  make install-dev   - Install dev dependencies"
	@echo "  make clean         - Clean temporary files"
	@echo ""
	@echo "Git:"
	@echo "  make setup-hooks   - Setup git hooks"
	@echo "  make pre-commit    - Run pre-commit checks"
	@echo "  make pre-push      - Run pre-push checks"

# Quick sanity tests (default for 'make test')
test:
	@./scripts/run_tests.sh sanity

test-quick:
	@./scripts/run_tests.sh sanity

# Full test suite with coverage
test-full:
	@./scripts/run_tests.sh full

# Release candidate tests
test-release:
	@./scripts/run_tests.sh release

# Integration tests
test-integration:
	@./scripts/run_tests.sh integration

# Run specific tests
test-specific:
	@if [ -z "$(PATTERN)" ]; then \
		echo "Usage: make test-specific PATTERN=<pattern>"; \
		exit 1; \
	fi
	@./scripts/run_tests.sh specific "$(PATTERN)"

# Install dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-mock pytest-asyncio pytest-xdist
	pip install ruff black isort

# Run linting
lint:
	@if command -v ruff &> /dev/null; then \
		echo "Running ruff..."; \
		ruff check src/; \
	else \
		echo "ruff not installed. Run: make install-dev"; \
	fi

# Format code
format:
	@if command -v black &> /dev/null; then \
		echo "Running black..."; \
		black src/; \
	else \
		echo "black not installed. Run: make install-dev"; \
	fi
	@if command -v isort &> /dev/null; then \
		echo "Running isort..."; \
		isort src/; \
	else \
		echo "isort not installed. Run: make install-dev"; \
	fi

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf htmlcov/
	rm -f coverage.xml
	rm -f .coverage

# Setup git hooks
setup-hooks:
	@echo "Setting up git hooks..."
	@if [ -d .git ]; then \
		git config core.hooksPath .githooks; \
		echo "✅ Git hooks configured to use .githooks/"; \
	else \
		echo "❌ Not a git repository"; \
		exit 1; \
	fi

# Run pre-commit checks manually
pre-commit:
	@./.githooks/pre-commit

# Run pre-push checks manually
pre-push:
	@./.githooks/pre-push

# Single command to run tests based on context
smart-test:
	@if [ -n "$$(git diff --cached --name-only)" ]; then \
		echo "📝 Detected staged changes - running sanity tests"; \
		make test-quick; \
	elif [ "$$(git rev-parse --abbrev-ref HEAD)" = "main" ] || [ "$$(git rev-parse --abbrev-ref HEAD)" = "master" ]; then \
		echo "🔒 On protected branch - running full tests"; \
		make test-full; \
	else \
		echo "🔧 On feature branch - running integration tests"; \
		make test-integration; \
	fi