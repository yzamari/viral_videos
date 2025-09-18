#!/bin/bash

# Stop all ViralAI Microservices

echo "🛑 Stopping ViralAI Microservices"
echo "================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to stop a service
stop_service() {
    local name=$1
    local port=$2
    
    echo -e "${YELLOW}Stopping $name...${NC}"
    
    # Try to read PID from file
    if [ -f "logs/microservices/${name}.pid" ]; then
        pid=$(cat logs/microservices/${name}.pid)
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            echo -e "${GREEN}✓ Stopped $name (PID: $pid)${NC}"
        fi
        rm -f logs/microservices/${name}.pid
    fi
    
    # Also kill by port as fallback
    lsof -ti:$port | xargs kill -9 2>/dev/null
}

# Stop all services
stop_service "Orchestrator" 8005
stop_service "Monitoring" 8003
stop_service "Video-Generator" 8002
stop_service "Prompt-Optimizer" 8001

echo ""
echo -e "${GREEN}All microservices stopped.${NC}"