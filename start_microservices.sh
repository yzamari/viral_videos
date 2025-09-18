#!/bin/bash

# ViralAI Microservices Startup Script
# Starts all microservices in separate processes

echo "🚀 Starting ViralAI Microservices Architecture"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create necessary directories
mkdir -p logs/microservices
mkdir -p /tmp/video_outputs

# Check if Redis is running
echo -e "${YELLOW}Checking Redis...${NC}"
if ! command -v redis-cli &> /dev/null; then
    echo -e "${RED}Redis is not installed. Please install Redis first.${NC}"
    echo "On macOS: brew install redis"
    echo "On Ubuntu: sudo apt-get install redis-server"
    exit 1
fi

# Start Redis if not running
if ! redis-cli ping &> /dev/null; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    redis-server --daemonize yes
    sleep 2
fi

echo -e "${GREEN}✓ Redis is running${NC}"

# Function to start a service
start_service() {
    local name=$1
    local port=$2
    local script=$3
    
    echo -e "${YELLOW}Starting $name on port $port...${NC}"
    
    # Kill any existing process on this port
    lsof -ti:$port | xargs kill -9 2>/dev/null
    
    # Start the service
    python3 $script > logs/microservices/${name}.log 2>&1 &
    local pid=$!
    
    # Wait a moment for the service to start
    sleep 2
    
    # Check if service is running
    if ps -p $pid > /dev/null; then
        echo -e "${GREEN}✓ $name started (PID: $pid)${NC}"
        echo $pid > logs/microservices/${name}.pid
    else
        echo -e "${RED}✗ Failed to start $name${NC}"
        return 1
    fi
}

# Start all microservices
echo ""
echo "Starting Microservices..."
echo "-------------------------"

# Start services in order of dependencies
start_service "Prompt-Optimizer" 8001 "src/microservices/prompt_optimizer/server.py"
start_service "Video-Generator" 8002 "src/microservices/video_generator/server.py"
start_service "Monitoring" 8003 "src/microservices/monitoring/server.py"
start_service "Orchestrator" 8005 "src/microservices/orchestrator/server.py"

echo ""
echo "============================================"
echo -e "${GREEN}All microservices started successfully!${NC}"
echo ""
echo "Service URLs:"
echo "  • Prompt Optimizer: http://localhost:8001"
echo "  • Video Generator:  http://localhost:8002"
echo "  • Monitoring:       http://localhost:8003 (Dashboard)"
echo "  • Orchestrator:     http://localhost:8005"
echo ""
echo "Monitoring Dashboard: http://localhost:8003"
echo ""
echo "To stop all services, run: ./stop_microservices.sh"
echo "To check status, run: ./status_microservices.sh"
echo ""