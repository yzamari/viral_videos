#!/bin/bash
# 🚀 Viral AI Video Generator - Full Stack Launcher
# Starts both frontend and backend servers

set -e

echo "🎬 Starting Viral AI Video Generator"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check npm
if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi

# Check Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
python3 -m pip install -r requirements.txt

# Install frontend dependencies
echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
cd frontend
npm install

# Build frontend
echo -e "${BLUE}🔨 Building frontend...${NC}"
npm run build

# Return to root directory
cd ..

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "🚀 Starting servers..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Start backend server
echo -e "${BLUE}🔧 Starting backend server on http://localhost:8000${NC}"
python3 src/api/main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend development server (optional, for development)
if [ "$1" = "--dev" ]; then
    echo -e "${BLUE}🎨 Starting frontend development server on http://localhost:5173${NC}"
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo -e "${GREEN}🎉 Both servers are running!${NC}"
    echo -e "${GREEN}📊 Backend API: http://localhost:8000${NC}"
    echo -e "${GREEN}📊 API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}🎨 Frontend Dev: http://localhost:5173${NC}"
    echo -e "${GREEN}🎬 Production App: http://localhost:8000${NC}"
else
    echo ""
    echo -e "${GREEN}🎉 Server is running!${NC}"
    echo -e "${GREEN}📊 Backend API: http://localhost:8000${NC}"
    echo -e "${GREEN}📊 API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}🎬 Web App: http://localhost:8000${NC}"
fi

echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "  - Use Ctrl+C to stop all servers"
echo "  - Run with --dev flag for development mode"
echo "  - Check logs in the terminal for any issues"
echo ""

# Wait for all background jobs
wait