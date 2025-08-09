#!/bin/bash

# ViralAI Platform Stop Script
# Stops all running servers

echo "
╔══════════════════════════════════════════╗
║      Stopping ViralAI Platform           ║
╚══════════════════════════════════════════╝
"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Stopping all ViralAI services...${NC}"

# Kill backend servers
echo -e "${YELLOW}Stopping backend API server...${NC}"
pkill -f "uvicorn.*main" 2>/dev/null
pkill -f "uvicorn.*main_test" 2>/dev/null

# Kill frontend servers
echo -e "${YELLOW}Stopping frontend dev server...${NC}"
pkill -f "vite" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null

# Kill any processes on standard ports
for port in 8770 5173 5174; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Killing process on port $port (PID: $pid)${NC}"
        kill -9 $pid 2>/dev/null
    fi
done

# Clean up log files
if [ -f "/tmp/backend.log" ]; then
    rm /tmp/backend.log
fi
if [ -f "/tmp/frontend.log" ]; then
    rm /tmp/frontend.log
fi

echo -e "${GREEN}✅ All ViralAI services stopped successfully${NC}"