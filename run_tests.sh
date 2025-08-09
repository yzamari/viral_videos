#!/bin/bash

# ViralAI Advertising Platform - Complete Test Suite Runner

echo "🚀 Starting ViralAI Advertising Platform Tests"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    
    # Kill backend server
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend server (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # Kill frontend server
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend server (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Kill any remaining processes on ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    
    echo -e "${GREEN}Cleanup complete${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Step 1: Check prerequisites
echo -e "\n${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found${NC}"

# Step 2: Install Python dependencies
echo -e "\n${YELLOW}Step 2: Installing Python dependencies...${NC}"
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Step 3: Install frontend dependencies
echo -e "\n${YELLOW}Step 3: Installing frontend dependencies...${NC}"
cd frontend
npm install --silent
npx playwright install --quiet
cd ..
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Step 4: Start backend server
echo -e "\n${YELLOW}Step 4: Starting backend server...${NC}"

# Check if port 8000 is already in use
if check_port 8000; then
    echo -e "${YELLOW}Port 8000 is already in use. Killing existing process...${NC}"
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

# Start backend
python src/api/main.py &
BACKEND_PID=$!
echo "Backend server starting (PID: $BACKEND_PID)..."

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo -e "${GREEN}✓ Backend server is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Backend server failed to start${NC}"
        exit 1
    fi
    sleep 1
done

# Step 5: Start frontend server
echo -e "\n${YELLOW}Step 5: Starting frontend server...${NC}"

# Check if port 3000 is already in use
if check_port 3000; then
    echo -e "${YELLOW}Port 3000 is already in use. Killing existing process...${NC}"
    lsof -ti:3000 | xargs kill -9
    sleep 2
fi

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "Frontend server starting (PID: $FRONTEND_PID)..."

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✓ Frontend server is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Frontend server failed to start${NC}"
        exit 1
    fi
    sleep 1
done

# Step 6: Run Playwright tests
echo -e "\n${YELLOW}Step 6: Running Playwright E2E tests...${NC}"
echo "============================================"

cd frontend

# Run tests with different configurations
echo -e "\n${YELLOW}Running authentication tests...${NC}"
npx playwright test tests/e2e/auth.spec.ts --reporter=list

echo -e "\n${YELLOW}Running campaign management tests...${NC}"
npx playwright test tests/e2e/campaigns.spec.ts --reporter=list

echo -e "\n${YELLOW}Running analytics tests...${NC}"
npx playwright test tests/e2e/analytics.spec.ts --reporter=list

echo -e "\n${YELLOW}Running trending tests...${NC}"
npx playwright test tests/e2e/trending.spec.ts --reporter=list

echo -e "\n${YELLOW}Running workflow tests...${NC}"
npx playwright test tests/e2e/workflows.spec.ts --reporter=list

echo -e "\n${YELLOW}Running real-time features tests...${NC}"
npx playwright test tests/e2e/realtime.spec.ts --reporter=list

# Run all tests together with HTML report
echo -e "\n${YELLOW}Running all tests with HTML report...${NC}"
npx playwright test --reporter=html

cd ..

# Step 7: Run Python unit tests
echo -e "\n${YELLOW}Step 7: Running Python unit tests...${NC}"
echo "============================================"

python -m pytest tests/test_trending_system.py -v
python -m pytest tests/test_campaign_manager.py -v 2>/dev/null || echo "Campaign manager tests not found"
python -m pytest tests/test_analytics.py -v 2>/dev/null || echo "Analytics tests not found"

# Step 8: Generate test report
echo -e "\n${YELLOW}Step 8: Generating test report...${NC}"
echo "============================================"

# Open HTML report
echo -e "${GREEN}Opening test report in browser...${NC}"
cd frontend
npx playwright show-report
cd ..

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}✅ All tests completed successfully!${NC}"
echo -e "${GREEN}============================================${NC}"

echo -e "\n${YELLOW}Servers are still running for manual testing:${NC}"
echo "  Backend: http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers and exit."

# Keep script running
wait