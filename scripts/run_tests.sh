#!/bin/bash
# Test runner script for ViralAI
# Provides different test suites for different scenarios

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if pytest is installed
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        print_color $RED "❌ pytest is not installed. Installing..."
        pip install pytest pytest-cov pytest-mock pytest-asyncio pytest-xdist
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ -d ".venv" ]; then
        print_color $BLUE "🔧 Activating virtual environment..."
        source .venv/bin/activate
    elif [ -d "venv" ]; then
        print_color $BLUE "🔧 Activating virtual environment..."
        source venv/bin/activate
    else
        print_color $YELLOW "⚠️  No virtual environment found, using system Python"
    fi
}

# Function to run sanity tests
run_sanity_tests() {
    print_color $BLUE "🧪 Running Sanity Tests (Quick Basic Tests)..."
    print_color $YELLOW "This will test core functionality only"
    
    # Run only critical unit tests with specific markers
    pytest tests/CI/ \
        -m "unit and not slow and not requires_api" \
        -k "test_core_decisions or test_video_generation or test_decision_framework" \
        --tb=short \
        -v \
        --maxfail=3 \
        --durations=10
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Sanity tests passed!"
        return 0
    else
        print_color $RED "❌ Sanity tests failed!"
        return 1
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_color $BLUE "🔗 Running Integration Tests..."
    
    pytest tests/CI/ \
        -m "integration and not requires_api" \
        --tb=short \
        -v \
        --maxfail=5
    
    return $?
}

# Function to run full test suite
run_full_tests() {
    print_color $BLUE "🚀 Running Full Test Suite..."
    print_color $YELLOW "This will run all tests including slow ones"
    
    # Run all tests with coverage
    pytest tests/CI/ \
        --cov=src \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-fail-under=95 \
        -v \
        --tb=short \
        --durations=20
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ All tests passed with >95% coverage!"
        print_color $BLUE "📊 Coverage report generated in htmlcov/index.html"
        return 0
    else
        print_color $RED "❌ Tests failed or coverage below 95%!"
        return 1
    fi
}

# Function to run release candidate tests
run_release_tests() {
    print_color $BLUE "🎯 Running Release Candidate Test Suite..."
    print_color $YELLOW "This will run comprehensive tests for release validation"
    
    # First, run linting
    print_color $BLUE "🔍 Running code quality checks..."
    if command -v ruff &> /dev/null; then
        ruff check src/
    else
        print_color $YELLOW "⚠️  ruff not installed, skipping linting"
    fi
    
    # Run all tests including slow and API tests (if credentials available)
    pytest tests/CI/ \
        --cov=src \
        --cov-report=html \
        --cov-report=xml \
        --cov-report=term-missing \
        --cov-fail-under=95 \
        -v \
        --tb=short \
        --durations=30 \
        --strict-markers
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Release candidate tests passed!"
        print_color $BLUE "📊 Coverage reports generated:"
        print_color $BLUE "   - HTML: htmlcov/index.html"
        print_color $BLUE "   - XML: coverage.xml"
        return 0
    else
        print_color $RED "❌ Release candidate tests failed!"
        return 1
    fi
}

# Function to run specific test file or pattern
run_specific_tests() {
    pattern=$1
    print_color $BLUE "🎯 Running tests matching: $pattern"
    
    pytest tests/CI/ -k "$pattern" -v --tb=short
    
    return $?
}

# Function to run tests by marker
run_marked_tests() {
    marker=$1
    print_color $BLUE "🏷️  Running tests marked as: $marker"
    
    pytest tests/CI/ -m "$marker" -v --tb=short
    
    return $?
}

# Main script logic
print_color $BLUE "==================================="
print_color $BLUE "    ViralAI Test Runner"
print_color $BLUE "==================================="

# Activate virtual environment
activate_venv

# Check pytest installation
check_pytest

# Parse command line arguments
case "${1:-sanity}" in
    "sanity"|"quick")
        print_color $GREEN "Mode: Sanity Tests (Quick)"
        run_sanity_tests
        ;;
    "integration")
        print_color $GREEN "Mode: Integration Tests"
        run_integration_tests
        ;;
    "full")
        print_color $GREEN "Mode: Full Test Suite"
        run_full_tests
        ;;
    "release"|"rc")
        print_color $GREEN "Mode: Release Candidate Tests"
        run_release_tests
        ;;
    "specific")
        if [ -z "$2" ]; then
            print_color $RED "❌ Please provide a test pattern"
            echo "Usage: $0 specific <pattern>"
            exit 1
        fi
        print_color $GREEN "Mode: Specific Tests"
        run_specific_tests "$2"
        ;;
    "mark")
        if [ -z "$2" ]; then
            print_color $RED "❌ Please provide a test marker"
            echo "Usage: $0 mark <marker>"
            echo "Available markers: unit, integration, e2e, slow, requires_api, requires_ffmpeg, gpu"
            exit 1
        fi
        print_color $GREEN "Mode: Marked Tests"
        run_marked_tests "$2"
        ;;
    *)
        print_color $RED "❌ Unknown test mode: $1"
        echo ""
        echo "Usage: $0 [mode] [options]"
        echo ""
        echo "Modes:"
        echo "  sanity|quick     - Run quick sanity tests (default)"
        echo "  integration      - Run integration tests"
        echo "  full            - Run full test suite with coverage"
        echo "  release|rc      - Run release candidate tests"
        echo "  specific <pat>  - Run tests matching pattern"
        echo "  mark <marker>   - Run tests with specific marker"
        echo ""
        echo "Examples:"
        echo "  $0 sanity                    # Quick tests before commit"
        echo "  $0 full                      # Full test suite"
        echo "  $0 release                   # Release validation"
        echo "  $0 specific test_veo         # Run VEO tests"
        echo "  $0 mark unit                 # Run unit tests only"
        exit 1
        ;;
esac

# Exit with the test result status
exit $?