#!/bin/bash

# Full Working Video Generator UI Launcher
echo "🎬 Launching Full Working Video Generator UI..."
echo "🔗 Opening at http://localhost:7860"
echo "📱 Use Ctrl+C to stop the server"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Launch the UI
python launch_full_working_app.py --ui 