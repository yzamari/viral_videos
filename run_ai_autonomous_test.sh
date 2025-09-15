#!/bin/bash

# AI-Autonomous Movie Generation Script
# Gives minimal mission - AI agents decide EVERYTHING else

echo "=================================================="
echo "🎬 AI-AUTONOMOUS MOVIE GENERATOR"
echo "=================================================="
echo "🤖 AI agents will:"
echo "   • Research real events"
echo "   • Decide what to show"
echo "   • Choose platform & duration"
echo "   • Determine visual style"
echo "   • Select music approach"
echo "=================================================="
echo ""

# Set API key if not already set
if [ -z "$GOOGLE_API_KEY" ]; then
    if [ -f "$HOME/.gemini_api_key" ]; then
        export GOOGLE_API_KEY=$(cat $HOME/.gemini_api_key)
        echo "✅ Loaded API key from ~/.gemini_api_key"
    else
        echo "❌ Error: Please set GOOGLE_API_KEY environment variable"
        echo "   Or create ~/.gemini_api_key file with your API key"
        exit 1
    fi
fi

# Clean up any stuck processes
echo "🧹 Cleaning up any stuck processes..."
pkill -f "test_ai_autonomous" 2>/dev/null || true

# Run the AI-autonomous generation
echo ""
echo "🚀 Starting AI-autonomous generation..."
echo "   Mission: Create 3-min Hollywood movie about Israel-Iran June 2025"
echo "   AI will research and decide everything else!"
echo ""

python3 test_ai_autonomous_movie.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Movie generation complete!"
    echo "📁 Check outputs/session_*/ for results"
else
    echo ""
    echo "❌ Generation failed. Check logs for details."
    exit 1
fi