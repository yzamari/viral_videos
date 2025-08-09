#!/bin/bash

# Start Test Servers Script
# Starts backend API and frontend for E2E testing

echo "🚀 Starting test servers for E2E testing..."

# Set test environment
export ENV_FILE=.env.test
export TEST_MODE=true

# Kill any existing servers
echo "Cleaning up existing processes..."
pkill -f "uvicorn src.api.main"
pkill -f "vite"
sleep 2

# Start backend API
echo "Starting backend API server..."
cd /Users/yahavzamari/viralAi
python3 -m uvicorn src.api.main:app --host localhost --port 8000 --reload &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        exit 1
    fi
    sleep 1
done

# Start frontend
echo "Starting frontend dev server..."
cd /Users/yahavzamari/viralAi/frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to start  
echo "Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start"
        kill $BACKEND_PID
        exit 1
    fi
    sleep 1
done

echo "✅ Both servers are running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop servers..."

# Keep script running and handle cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    pkill -f "uvicorn src.api.main"
    pkill -f "vite"
    echo "✅ Servers stopped"
}

trap cleanup EXIT

# Wait for user to stop
while true; do
    sleep 1
done