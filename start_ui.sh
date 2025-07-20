#!/bin/bash
# 🎬 Simple UI Launcher for Viral AI Video Generator
# Just starts the backend server

echo "🎬 Starting Viral AI Video Generator UI"
echo "======================================="

# Check if we're in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Please activate your virtual environment first:"
    echo "   source .venv/bin/activate"
    exit 1
fi

# Start backend server
echo "🔧 Starting backend server..."
echo "🌐 Web UI will be available at: http://localhost:8000"
echo "📊 API Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================="

# Start the backend server
python3 backend_server.py