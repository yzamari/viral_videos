#!/bin/bash

# 🎬 Viral Video Generator - Launch Script
# Simple script that actually works

echo "🎬 Starting Basic UI..."
echo "=================================="

# Set the API key
export GOOGLE_API_KEY=AIzaSyCtw5XG_XTbxxNRajkbGWj9feoaqwFoptA

# Navigate to the correct directory
cd /Users/yahavzamari/viralAi/viral-video-generator

# Check if we're in the right directory
if [ ! -f "simple_working_ui.py" ]; then
    echo "❌ Error: simple_working_ui.py not found"
    exit 1
fi

# Launch the simple working UI
echo "🚀 Launching Simple Working UI..."
echo "🌐 Interface will be available at: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

python basic_ui.py 