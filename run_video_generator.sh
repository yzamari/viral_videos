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

# Check API key
echo "🔐 Checking API key..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not found in environment variables"
    echo "Please set your API key: export GEMINI_API_KEY='your-key-here'"
    echo "Or create a .env file with GEMINI_API_KEY=your-key-here"
fi

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
PLATFORM="tiktok"
CATEGORY="Educational"
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
    echo "🚀 Launching Unified Real-time UI with Modern Text Overlays..."
    echo "🌐 Interface will be available at http://localhost:7860"
    echo "✅ Mission-based video generation ready"
    echo "🤖 Live agent discussions with real-time visualization"
    echo "🎬 VEO-2/VEO-3 integration with modern text overlays"
    echo "📊 Complete session tracking and analytics"
    echo "🎨 Modern social media fonts and smart positioning"
    echo "📱 Mobile-optimized for viral content"
    echo ""
    echo "🔄 Starting Gradio server..."
    python unified_realtime_ui.py
elif [ "$CLI_MODE" = true ]; then
    echo "🚀 Launching CLI Mode..."
    if [ -z "$MISSION" ]; then
        echo "❌ Error: Mission is required for CLI mode"
        echo "Usage: $0 cli --mission 'your mission here'"
        exit 1
    fi
    python main.py generate --topic "$MISSION" --duration "$DURATION" --platform "$PLATFORM" --category "$CATEGORY" --image-only
else
    echo "Usage: $0 [ui|cli] [options]"
    echo ""
    echo "🎬 UI Mode (Recommended):"
    echo "  $0 ui                    # Launch real-time web interface"
    echo "                           # - Watch AI agents discuss in real-time"
    echo "                           # - Modern social media text overlays"
    echo "                           # - In-browser video playback"
    echo "                           # - Smart positioning to avoid hiding content"
    echo ""
    echo "⚡ CLI Mode:"
    echo "  $0 cli --mission 'text'  # Generate via command line"
    echo "  Options:"
    echo "    --mission TEXT         # Mission to accomplish (required)"
    echo "    --duration N           # Duration in seconds (default: 15)"
    echo "    --platform PLATFORM    # tiktok/youtube/instagram (default: tiktok)"
    echo "    --category CATEGORY    # Educational/Business/Entertainment (default: Educational)"
    echo "    --no-discussions       # Disable AI agent discussions"
    echo ""
    echo "🎯 Examples:"
    echo "  $0 ui"
    echo "  $0 cli --mission 'toys are bad for bed'"
    echo "  $0 cli --mission 'shake bar day and night modes' --duration 30 --platform tiktok"
    echo ""
    echo "✨ Features:"
    echo "  - Modern social media fonts (Impact, Arial Black, Helvetica-Bold)"
    echo "  - Smart text positioning (never hides important content)"
    echo "  - Drop shadow effects for better readability"
    echo "  - Vibrant colors optimized for mobile engagement"
    echo "  - Real-time AI agent discussions"
    echo "  - VEO-2/VEO-3 video generation with fallbacks"
fi 