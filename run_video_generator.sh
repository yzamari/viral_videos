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
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Setting up Google Cloud authentication..."
    gcloud auth application-default login --no-browser
fi

# Parse command line arguments
UI_MODE=false
CLI_MODE=false
MISSION=""
DURATION=15
PLATFORM="youtube"
CATEGORY="Comedy"
DISCUSSIONS=true

while [[ $# -gt 0 ]]; do
    case $1 in
        ui|--ui)
            UI_MODE=true
            shift
            ;;
        cli|--cli)
            CLI_MODE=true
            shift
            ;;
        --mission)
            MISSION="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --no-discussions)
            DISCUSSIONS=false
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Launch appropriate mode
if [ "$UI_MODE" = true ]; then
    echo "🚀 Launching Unified Real-time UI..."
    echo "🌐 Interface will be available at http://localhost:7860"
    echo "✅ Mission-based video generation ready"
    echo "🤖 Live agent discussions with real-time visualization"
    echo "🎬 VEO-2/VEO-3 integration with fallback systems"
    echo "📊 Complete session tracking and analytics"
    python unified_realtime_ui.py --port 7860
elif [ "$CLI_MODE" = true ]; then
    echo "🚀 Launching CLI Mode..."
    if [ -z "$MISSION" ]; then
        echo "❌ Error: Mission is required for CLI mode"
        echo "Usage: $0 cli --mission 'your mission here'"
        exit 1
    fi
    python unified_realtime_ui.py --mission "$MISSION" --duration "$DURATION" --platform "$PLATFORM" --category "$CATEGORY" --discussions "$DISCUSSIONS"
else
    echo "Usage: $0 [ui|cli] [options]"
    echo ""
    echo "UI Mode:"
    echo "  $0 ui                    # Launch web interface"
    echo ""
    echo "CLI Mode:"
    echo "  $0 cli --mission 'text'  # Generate via command line"
    echo "  Options:"
    echo "    --mission TEXT         # Mission to accomplish (required)"
    echo "    --duration N           # Duration in seconds (default: 15)"
    echo "    --platform PLATFORM    # youtube/tiktok/instagram (default: youtube)"
    echo "    --category CATEGORY    # Comedy/Entertainment/Education (default: Comedy)"
    echo "    --no-discussions       # Disable AI agent discussions"
    echo ""
    echo "Examples:"
    echo "  $0 ui"
    echo "  $0 cli --mission 'inspire people to learn coding'"
    echo "  $0 cli --mission 'get viewers excited about science' --duration 30 --platform tiktok"
fi 