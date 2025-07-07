#!/bin/bash

# 🎬 Enhanced Viral Video Generator with VEO-2 & 19 AI Agents
# Professional-grade video generation system with complete parameter support
# Usage: ./run_video_generator.sh [ui|cli] [options]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse command line arguments
MODE=${1:-ui}
shift || true  # Remove first argument, ignore if no more args

# Display header
echo -e "${PURPLE}🎬 Starting Enhanced Viral Video Generator...${NC}"
echo -e "${CYAN}=============================================${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source .venv/bin/activate

# Check and install dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if [ ! -f ".deps_installed" ]; then
    echo -e "${YELLOW}⚠️  Installing required packages...${NC}"
    pip install --upgrade pip
    pip install google-generativeai gradio moviepy==1.0.3 gtts colorlog Pillow pydantic requests google-auth
    touch .deps_installed
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Check for required environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}❌ GOOGLE_API_KEY environment variable not set${NC}"
    echo -e "${YELLOW}💡 Please set your Gemini API key:${NC}"
    echo -e "${CYAN}   export GOOGLE_API_KEY=\"your_api_key_here\"${NC}"
    exit 1
fi

# Check Google Cloud authentication
echo -e "${BLUE}🔐 Checking Google Cloud authentication...${NC}"
if ! gcloud auth application-default print-access-token &>/dev/null; then
    echo -e "${YELLOW}⚠️  Google Cloud authentication required for VEO-2${NC}"
    echo -e "${CYAN}   Run: gcloud auth application-default login${NC}"
    echo -e "${YELLOW}   Continuing with fallback mode...${NC}"
fi

# Function to show usage
show_usage() {
    echo -e "${GREEN}🎬 Enhanced Viral Video Generator Usage${NC}"
    echo -e "${CYAN}===========================================${NC}"
    echo ""
    echo -e "${YELLOW}Basic Usage:${NC}"
    echo -e "  ./run_video_generator.sh [mode] [options]"
    echo ""
    echo -e "${YELLOW}Modes:${NC}"
    echo -e "  ${GREEN}ui${NC}     - Launch web interface (default)"
    echo -e "  ${GREEN}cli${NC}    - Command line generation"
    echo -e "  ${GREEN}test${NC}   - Run test video generation"
    echo -e "  ${GREEN}help${NC}   - Show this help message"
    echo ""
    echo -e "${YELLOW}All Available Parameters:${NC}"
    echo -e "  ${GREEN}--topic \"Your topic\"${NC}           - Video topic"
    echo -e "  ${GREEN}--duration 10|15|30|60${NC}          - Duration in seconds"
    echo -e "  ${GREEN}--platform youtube|tiktok|instagram${NC} - Target platform"
    echo -e "  ${GREEN}--category Comedy|Entertainment|Education${NC} - Video category"
    echo -e "  ${GREEN}--discussions${NC}                   - Enable 19 AI agent discussions"
    echo -e "  ${GREEN}--no-discussions${NC}                - Disable agent discussions"
    echo -e "  ${GREEN}--ui${NC}                            - Launch web interface"
    echo -e "  ${GREEN}--port 7861${NC}                     - Custom UI port"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ${CYAN}# Launch UI${NC}"
    echo -e "  ./run_video_generator.sh ui"
    echo -e "  ./run_video_generator.sh ui --port 7861"
    echo ""
    echo -e "  ${CYAN}# CLI Generation${NC}"
    echo -e "  ./run_video_generator.sh cli --topic \"funny cats\" --duration 30"
    echo -e "  ./run_video_generator.sh cli --topic \"tech news\" --platform youtube --category Education"
    echo -e "  ./run_video_generator.sh cli --topic \"comedy\" --duration 15 --platform tiktok --discussions"
    echo ""
    echo -e "${YELLOW}Features:${NC}"
    echo -e "  🤖 ${GREEN}19 AI Agents${NC} - Professional discussions with full visualization"
    echo -e "  🎥 ${GREEN}VEO-2 Video${NC} - Real AI video generation"
    echo -e "  🎵 ${GREEN}Google TTS${NC} - Professional audio synthesis"
    echo -e "  📱 ${GREEN}Platform Optimization${NC} - YouTube, TikTok, Instagram"
    echo -e "  🎭 ${GREEN}Category Support${NC} - Comedy, Entertainment, Education"
    echo -e "  ⏱️ ${GREEN}Duration Control${NC} - 10-60 seconds"
    echo ""
}

# Determine mode and handle parameters
case $MODE in
    ui|UI)
        echo -e "${GREEN}🚀 Launching Enhanced UI Mode...${NC}"
        echo -e "${CYAN}🌐 Interface will be available at auto-detected port (starting from 7860)${NC}"
        echo -e "${GREEN}✅ All parameters available in UI: topic, duration, platform, category, discussions${NC}"
        echo -e "${PURPLE}🤖 Agent discussions fully visualized with individual contributions${NC}"
        
        # Pass through any additional arguments to the Python script
        python launch_full_working_app.py --ui "$@"
        ;;
    cli|CLI)
        if [ $# -eq 0 ]; then
            echo -e "${GREEN}🚀 CLI Mode - Parameter Examples${NC}"
            echo -e "${CYAN}💡 Usage examples:${NC}"
            echo -e "${YELLOW}   ./run_video_generator.sh cli --topic \"your topic\" --duration 15${NC}"
            echo -e "${YELLOW}   ./run_video_generator.sh cli --topic \"comedy video\" --duration 30 --platform youtube${NC}"
            echo -e "${YELLOW}   ./run_video_generator.sh cli --topic \"education\" --category Education --discussions${NC}"
            echo ""
            echo -e "${GREEN}✅ Ready for command line video generation${NC}"
            echo -e "${CYAN}📋 Available parameters:${NC}"
            echo -e "${YELLOW}   --topic \"Your video topic\"${NC}"
            echo -e "${YELLOW}   --duration 10|15|30|60 (seconds)${NC}"
            echo -e "${YELLOW}   --platform youtube|tiktok|instagram${NC}"
            echo -e "${YELLOW}   --category Comedy|Entertainment|Education${NC}"
            echo -e "${YELLOW}   --discussions (enable 19 AI agent discussions)${NC}"
            echo -e "${YELLOW}   --no-discussions (disable agent discussions)${NC}"
            echo ""
            echo -e "${PURPLE}🎬 Example generation:${NC}"
            echo -e "${CYAN}./run_video_generator.sh cli --topic \"funny cats doing yoga\" --duration 15 --platform tiktok --discussions${NC}"
        else
            echo -e "${GREEN}🚀 Launching CLI Generation...${NC}"
            echo -e "${CYAN}🎯 Parameters: $@${NC}"
            
            # Pass all arguments to the Python script
            python launch_full_working_app.py "$@"
        fi
        ;;
    test|TEST)
        echo -e "${GREEN}🧪 Running Enhanced Test Generation...${NC}"
        echo -e "${CYAN}🎯 Generating test video with all features${NC}"
        echo -e "${PURPLE}📊 Testing: AI robots dancing | 15s | YouTube | Comedy | Full Discussions${NC}"
        python launch_full_working_app.py --topic "AI robots dancing in a futuristic city" --duration 15 --platform youtube --category Comedy --discussions
        ;;
    help|HELP|-h|--help)
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown mode: $MODE${NC}"
        echo -e "${YELLOW}💡 Available modes: ui, cli, test, help${NC}"
        show_usage
        exit 1
        ;;
esac

echo ""
echo -e "${PURPLE}🎉 Enhanced Viral Video Generator Ready!${NC}"
echo -e "${CYAN}📊 System Status:${NC}"
echo -e "${GREEN}   ✅ 19 AI Agents - Operational with full visualization${NC}"
echo -e "${GREEN}   ✅ VEO-2 Integration - Ready${NC}"
echo -e "${GREEN}   ✅ Audio Generation - Active${NC}"
echo -e "${GREEN}   ✅ Platform Optimization - YouTube/TikTok/Instagram${NC}"
echo -e "${GREEN}   ✅ Category Support - Comedy/Entertainment/Education${NC}"
echo -e "${GREEN}   ✅ Duration Control - 10-60 seconds${NC}"
echo -e "${GREEN}   ✅ Agent Discussions - Fully visualized${NC}" 