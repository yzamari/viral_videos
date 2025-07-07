#!/bin/bash

# 🎬 Viral Video Generator - Launch Script
# Simple script that actually works

echo "🎬 Starting Video Generator..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "launch_full_working_app.py" ]; then
    echo "❌ Error: launch_full_working_app.py not found"
    echo "Please run this script from the viralAi directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not set"
    echo "Loading from .env file if available..."
fi

# Launch the enhanced video generator
echo "🚀 Launching Enhanced Video Generator..."
echo "🌐 Interface will be available at: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

python launch_full_working_app.py "$@" 