# ViralAI Testing Guide

## Overview

This guide explains how to run tests for the ViralAI project. We have different test suites for different scenarios to ensure code quality while maintaining developer productivity.

## Quick Start

### Single Command for All Tests

```bash
# Run appropriate tests for your current context
make smart-test
```

This command automatically determines which tests to run based on:
- If you have staged changes → runs sanity tests
- If you're on main/master branch → runs full tests
- If you're on a feature branch → runs integration tests

### Manual Test Commands

```bash
# Quick sanity tests (before commit)
make test

# Full test suite with coverage
make test-full

# Release candidate tests
make test-release

# Run specific tests
make test-specific PATTERN=test_veo
```

## Test Levels

### 1. Sanity Tests (Quick) 🧪
**When to use**: Before every commit
**Duration**: ~30 seconds
**Command**: `make test` or `./scripts/run_tests.sh sanity`

Tests:
- Core decision framework
- Basic video generation
- Critical functionality only

### 2. Integration Tests 🔗
**When to use**: Before pushing to feature branches
**Duration**: ~2-3 minutes
**Command**: `make test-integration`

Tests:
- Component interactions
- API integrations (mocked)
- End-to-end workflows

### 3. Full Test Suite 🚀
**When to use**: Before merging to main
**Duration**: ~5-10 minutes
**Command**: `make test-full`

Tests:
- All unit tests
- All integration tests
- Coverage report (must be >95%)

### 4. Release Candidate Tests 🎯
**When to use**: Before creating a release
**Duration**: ~10-15 minutes
**Command**: `make test-release`

Tests:
- Everything in full suite
- Code quality checks (linting)
- Performance tests
- API tests (if credentials available)

## Git Integration

### Setup Git Hooks

```bash
# Enable automatic testing on commit/push
make setup-hooks
```

This configures:
- **pre-commit**: Runs sanity tests before commit
- **pre-push**: Runs integration/full tests before push

### Manual Hook Execution

```bash
# Test what pre-commit would do
make pre-commit

# Test what pre-push would do
make pre-push
```

## Test Organization

```
tests/CI/
├── conftest.py                    # Shared fixtures
├── test_video_generation/         # Video generation tests
├── test_ai_agents/               # AI agent tests
├── test_social_media/            # Social media tests
├── test_multilanguage/           # Multi-language tests
├── test_audio/                   # Audio system tests
├── test_overlays/                # Overlay system tests
├── test_session/                 # Session management tests
├── test_decision/                # Decision framework tests
├── test_config/                  # Configuration tests
├── test_themes/                  # Theme system tests
├── test_styles/                  # Style reference tests
├── test_characters/              # Character consistency tests
└── test_integration/             # End-to-end tests
```

## Running Specific Tests

### By Pattern
```bash
# Run all VEO-related tests
./scripts/run_tests.sh specific test_veo

# Run all agent tests
./scripts/run_tests.sh specific test_agent

# Using make
make test-specific PATTERN=test_decision
```

### By Marker
```bash
# Run only unit tests
./scripts/run_tests.sh mark unit

# Run only integration tests
./scripts/run_tests.sh mark integration

# Run tests that don't require API
./scripts/run_tests.sh mark "not requires_api"
```

### Available Markers
- `unit` - Fast, isolated unit tests
- `integration` - Component integration tests
- `e2e` - End-to-end tests
- `slow` - Tests that take >5 seconds
- `requires_api` - Tests requiring external API access
- `requires_ffmpeg` - Tests requiring ffmpeg
- `gpu` - Tests requiring GPU

## Coverage Reports

After running full or release tests:

```bash
# View HTML coverage report
open htmlcov/index.html

# Coverage files generated:
# - htmlcov/ - HTML report
# - coverage.xml - XML report for CI
# - .coverage - Raw coverage data
```

## Writing Tests

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestFeatureName:
    """Test suite for FeatureName"""
    
    @pytest.fixture
    def setup_data(self):
        """Setup test data"""
        return {"test": "data"}
    
    @pytest.mark.unit
    def test_unit_functionality(self, setup_data):
        """Test basic functionality"""
        assert True
    
    @pytest.mark.integration
    def test_integration_workflow(self, mock_session_context):
        """Test integration with other components"""
        assert True
    
    @pytest.mark.slow
    @pytest.mark.requires_api
    def test_external_api(self):
        """Test requiring external API"""
        pytest.skip("Requires API credentials")
```

### Using Fixtures

Common fixtures available in `conftest.py`:
- `temp_dir` - Temporary directory
- `mock_session_manager` - Mocked session manager
- `mock_core_decisions` - Mocked decisions object
- `mock_ai_client` - Mocked AI client
- `sample_script_segments` - Sample script data

## CI/CD Integration

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: make install-dev
      - name: Run tests
        run: make test-full
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Local CI Simulation
```bash
# Simulate what CI would run
make clean
make install-dev
make test-release
```

## Troubleshooting

### Tests Failing Locally but Not in CI
1. Check virtual environment: `which python`
2. Clear cache: `make clean`
3. Reinstall dependencies: `make install-dev`

### Slow Tests
```bash
# Identify slow tests
pytest tests/CI/ --durations=10

# Skip slow tests
pytest tests/CI/ -m "not slow"
```

### Coverage Below 95%
```bash
# See what's not covered
pytest tests/CI/ --cov=src --cov-report=term-missing

# Generate detailed HTML report
make test-full
open htmlcov/index.html
```

### API Tests
```bash
# Set credentials for API tests
export GOOGLE_API_KEY="your-key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/creds.json"

# Run including API tests
pytest tests/CI/ -m "requires_api"
```

## Best Practices

1. **Always run tests before committing**
   ```bash
   make test  # Quick sanity check
   ```

2. **Use appropriate test level**
   - Quick fixes → sanity tests
   - New features → integration tests
   - Before release → full suite

3. **Keep tests fast**
   - Mock external dependencies
   - Use `@pytest.mark.slow` for slow tests
   - Parallelize with pytest-xdist

4. **Maintain coverage**
   - Target: 100% for implemented features
   - Minimum: 95% overall
   - Exclude only unimplemented features

5. **Write tests first (TDD)**
   - Write test for new feature
   - See it fail
   - Implement feature
   - See test pass

## Summary Commands

```bash
# Developer workflow
make test              # Before commit (30s)
git commit -m "msg"    # Auto-runs sanity tests
make test-integration  # Before push (2-3m)
git push              # Auto-runs appropriate tests

# Release workflow
make test-full        # Full validation (5-10m)
make test-release     # Final checks (10-15m)
git tag -a v1.0.0    # Tag release
git push --tags      # Push release
```

For more details, see the [test implementation](../tests/CI/README.md).