#!/bin/bash

# ViralAI Platform Startup Script
# Starts both backend API and frontend development servers

echo "
╔══════════════════════════════════════════╗
║       ViralAI Platform Launcher          ║
║   AI-Powered Video Generation Studio     ║
╚══════════════════════════════════════════╝
"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_PORT=8770
FRONTEND_PORT=5173
PROJECT_DIR="/Users/yahavzamari/viralAi"

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i:$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Killing process on port $port (PID: $pid)...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
    fi
}

# Clean up function
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Clean up any remaining processes
    pkill -f "uvicorn.*main" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    
    echo -e "${GREEN}✅ Servers stopped successfully${NC}"
    exit 0
}

# Set up trap for clean exit
trap cleanup INT TERM EXIT

# Check and clean ports
echo -e "${BLUE}🔍 Checking ports...${NC}"

if check_port $BACKEND_PORT; then
    echo -e "${YELLOW}Port $BACKEND_PORT is in use${NC}"
    kill_port $BACKEND_PORT
fi

if check_port $FRONTEND_PORT; then
    echo -e "${YELLOW}Port $FRONTEND_PORT is in use${NC}"
    kill_port $FRONTEND_PORT
fi

# Start Backend API
echo -e "${BLUE}🚀 Starting Backend API Server...${NC}"
cd "$PROJECT_DIR"

# Always use the main API with video generation endpoints
echo -e "${YELLOW}Using video generation API (main.py) with real CLI integration${NC}"
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > /tmp/backend.log 2>&1 &

BACKEND_PID=$!

# Wait for backend to start
echo -e "${BLUE}⏳ Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend API is running at http://localhost:$BACKEND_PORT${NC}"
        echo -e "${GREEN}   API Docs: http://localhost:$BACKEND_PORT/docs${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start. Check logs at /tmp/backend.log${NC}"
        tail -20 /tmp/backend.log
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# Start Frontend
echo -e "${BLUE}🎨 Starting Frontend Development Server...${NC}"
cd "$PROJECT_DIR/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Start frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo -e "${BLUE}⏳ Waiting for frontend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is running at http://localhost:$FRONTEND_PORT${NC}"
        break
    elif curl -s http://localhost:5174 > /dev/null 2>&1; then
        FRONTEND_PORT=5174
        echo -e "${GREEN}✅ Frontend is running at http://localhost:$FRONTEND_PORT${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Frontend failed to start. Check logs at /tmp/frontend.log${NC}"
        tail -20 /tmp/frontend.log
        exit 1
    fi
    sleep 1
    echo -n "."
done
echo ""

# Success message
echo -e "
${GREEN}╔══════════════════════════════════════════════════╗
║         🎉 ViralAI Platform is Ready!            ║
╚══════════════════════════════════════════════════╝${NC}

${BLUE}📱 Access the application:${NC}
   ${GREEN}➜${NC} Frontend:  http://localhost:$FRONTEND_PORT
   ${GREEN}➜${NC} Backend:   http://localhost:$BACKEND_PORT
   ${GREEN}➜${NC} API Docs:  http://localhost:$BACKEND_PORT/docs

${BLUE}🔐 Test Credentials:${NC}
   Username: testuser
   Password: testpass123

${BLUE}🛠 Features Available:${NC}
   • Content Generator - Create custom AI videos
   • News Generator - Aggregate news from sources
   • Professional UI with dark/light modes
   • Real-time progress monitoring

${YELLOW}Press Ctrl+C to stop all servers${NC}
"

# Monitor logs
echo -e "${BLUE}📊 Monitoring servers (showing recent logs)...${NC}"
echo "============================================"

# Keep the script running
while true; do
    sleep 5
    
    # Check if servers are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend server crashed! Check /tmp/backend.log${NC}"
        tail -10 /tmp/backend.log
        exit 1
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend server crashed! Check /tmp/frontend.log${NC}"
        tail -10 /tmp/frontend.log
        exit 1
    fi
done