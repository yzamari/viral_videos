#!/bin/bash

# 🎬 Unified Real-time VEO-2 Video Generator Launch Script
# This is the ONLY script you need to run the complete system

echo "🎬 Starting Unified Real-time VEO-2 Video Generator..."
echo "============================================================="

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Check dependencies
echo "📦 Checking dependencies..."
python -c "import gradio, google.generativeai" 2>/dev/null || {
    echo "📦 Installing missing dependencies..."
    pip install -r requirements.txt
}

# Check Google Cloud authentication
echo "🔐 Checking Google Cloud authentication..."
gcloud auth application-default print-access-token >/dev/null 2>&1 || {
    echo "🔐 Setting up Google Cloud authentication..."
    gcloud auth application-default login --no-browser
}

# Determine mode
MODE=${1:-ui}

if [ "$MODE" = "ui" ]; then
    echo "🚀 Launching Unified Real-time UI..."
    echo "🌐 Interface will be available at http://localhost:7860"
    echo "✅ Mission-based video generation ready"
    echo "🤖 Live agent discussions with real-time visualization"
    echo "🎬 VEO-2/VEO-3 integration with fallback systems"
    echo "📊 Complete session tracking and analytics"
    
    python unified_realtime_ui.py --port 7860
    
elif [ "$MODE" = "cli" ]; then
    echo "🚀 Launching Command Line Mode..."
    echo "🎯 Mission: ${2:-convince all the kids to love Mango}"
    echo "⏱️ Duration: ${3:-15}s"
    echo "📱 Platform: ${4:-youtube}"
    echo "🎭 Category: ${5:-Comedy}"
    
    python launch_full_working_app.py \
        --mission "${2:-convince all the kids to love Mango}" \
        --duration ${3:-15} \
        --platform ${4:-youtube} \
        --category ${5:-Comedy}
else
    echo "Usage: $0 [ui|cli] [mission] [duration] [platform] [category]"
    echo ""
    echo "Examples:"
    echo "  $0 ui                                    # Launch web interface"
    echo "  $0 cli \"get kids to love vegetables\"    # CLI generation"
    echo ""
    exit 1
fi 