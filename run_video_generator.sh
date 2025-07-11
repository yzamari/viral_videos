#!/bin/bash

# 🎬 AI Video Generator Launch Script
# Launch the working AI video generator with intelligent agents

echo "🎬 Starting AI Video Generator with Intelligent Agents..."
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
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not found in environment variables"
    echo "Please set your API key: export GOOGLE_API_KEY='your-key-here'"
    echo "Or create a .env file with GOOGLE_API_KEY=your-key-here"
fi

# Parse command line arguments
UI_MODE=false
CLI_MODE=false
MISSION=""
DURATION=15
PLATFORM="tiktok"
CATEGORY="Educational"
DISCUSSIONS="enhanced"

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
        --discussions)
            DISCUSSIONS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Launch appropriate mode
if [ "$UI_MODE" = true ]; then
    echo "🚀 Launching Modern UI with AI Agents..."
    echo "🌐 Interface will be available at http://localhost:7860"
    echo "✅ AI-powered video generation ready"
    echo "🤖 Intelligent voice selection and style decisions"
    echo "🎬 VEO2/VEO3/Image generation with smart fallbacks"
    echo "📊 Complete AI agent integration"
    echo "🎨 Smart positioning and visual style selection"
    echo "📱 Mobile-optimized for viral content"
    echo ""
    echo "🔄 Starting Gradio server..."
    python modern_ui.py
elif [ "$CLI_MODE" = true ]; then
    echo "🚀 Launching CLI Mode with AI Agents..."
    if [ -z "$MISSION" ]; then
        echo "❌ Error: Mission is required for CLI mode"
        echo "Usage: $0 cli --mission 'your mission here'"
        exit 1
    fi
    python main.py generate --mission "$MISSION" --duration "$DURATION" --platform "$PLATFORM" --category "$CATEGORY" --discussions "$DISCUSSIONS"
else
    echo "Usage: $0 [ui|cli] [options]"
    echo ""
    echo "🎬 UI Mode (Recommended):"
    echo "  $0 ui                    # Launch modern web interface"
    echo "                           # - AI voice selection interface"
    echo "                           # - Visual style and positioning controls"
    echo "                           # - Real-time generation progress"
    echo "                           # - Smart AI agent decisions"
    echo ""
    echo "⚡ CLI Mode:"
    echo "  $0 cli --mission 'text'    # Generate via command line"
    echo "  Options:"
    echo "    --mission TEXT         # Video mission (required)"
    echo "    --duration N           # Duration in seconds (default: 15)"
    echo "    --platform PLATFORM    # tiktok/youtube/instagram (default: tiktok)"
    echo "    --category CATEGORY    # Educational/Comedy/Entertainment (default: Educational)"
    echo "    --discussions MODE     # enhanced/streamlined/off (default: enhanced)"
    echo ""
    echo "🎯 Examples:"
    echo "  $0 ui"
    echo "  $0 cli --mission 'Create awareness about quantum computing breakthroughs'"
    echo "  $0 cli --mission 'Make people laugh with funny cat video explanations' --duration 30 --platform tiktok"
    echo ""
    echo "✨ AI Agent Features:"
    echo "  - 🎤 VoiceDirectorAgent: Smart voice selection (8 personalities)"
    echo "  - 🎨 VisualStyleAgent: Dynamic style decisions (10+ styles)"
    echo "  - 🎯 OverlayPositioningAgent: Smart subtitle positioning"
    echo "  - 📝 EnhancedScriptProcessor: Punctuation & TTS optimization"
    echo "  - 🌍 MultilingualTTS: 14+ language support"
    echo "  - 🔄 ContinuityDecisionAgent: Frame continuity decisions"
fi 