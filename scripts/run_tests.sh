#!/bin/bash
# ViralAI Testing Suite v2.5.0-rc1
# Comprehensive test runner for all test types

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ViralAI Testing Suite v2.5.0-rc1${NC}"
echo "=========================================="

# Function to run tests with proper error handling
run_test_suite() {
    local test_type=$1
    local test_path=$2
    local description=$3
    
    echo -e "\n${YELLOW}📋 Running ${description}...${NC}"
    
    if [ -d "$test_path" ]; then
        cd "$(dirname "$0")/.."
        python -m pytest "$test_path" -v --tb=short
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ ${description} PASSED${NC}"
        else
            echo -e "${RED}❌ ${description} FAILED${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  ${description} directory not found: $test_path${NC}"
    fi
}

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  No virtual environment detected. Consider activating one.${NC}"
fi

# Check dependencies
echo -e "${BLUE}🔍 Checking dependencies...${NC}"
python -c "import pytest, moviepy, google.cloud" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Missing dependencies. Run: pip install -r requirements.txt${NC}"
    exit 1
fi

# Run test suites
echo -e "${BLUE}🧪 Starting test execution...${NC}"

# 1. Unit Tests
run_test_suite "unit" "tests_organized/unit" "Unit Tests"

# 2. Integration Tests  
run_test_suite "integration" "tests_organized/integration" "Integration Tests"

# 3. E2E Tests
run_test_suite "e2e" "tests_organized/e2e" "End-to-End Tests"

# 4. Comprehensive Tests
run_test_suite "comprehensive" "tests_organized/comprehensive" "Comprehensive Tests"

# 5. Quick System Test
echo -e "\n${YELLOW}📋 Running Quick System Test...${NC}"
cd "$(dirname "$0")/.."
timeout 60 python main.py generate --mission "test system health" --platform instagram --duration 6 --cheap --cheap-mode full >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Quick System Test PASSED${NC}"
else
    echo -e "${RED}❌ Quick System Test FAILED${NC}"
fi

echo -e "\n${GREEN}🎉 All tests completed!${NC}"
echo -e "${BLUE}📊 Test Summary: Check individual test results above${NC}"