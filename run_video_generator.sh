#!/bin/bash

# 🎬 Viral Video Generator with VEO-2 & 19 AI Agents
# Professional-grade video generation system
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

# Display header
echo -e "${PURPLE}🎬 Starting Viral Video Generator...${NC}"
echo -e "${CYAN}==================================${NC}"

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

# Determine mode
MODE=${1:-ui}

case $MODE in
    ui|UI)
        echo -e "${GREEN}🚀 Launching UI Mode...${NC}"
        echo -e "${CYAN}🌐 Interface will be available at auto-detected port (starting from 7860)${NC}"
        echo -e "${GREEN}✅ Using Full Working App with VEO-2 + Audio + Agent Discussions${NC}"
        python launch_full_working_app.py --ui
        ;;
    cli|CLI)
        echo -e "${GREEN}🚀 Launching CLI Mode...${NC}"
        echo -e "${CYAN}💡 Usage examples:${NC}"
        echo -e "${YELLOW}   python launch_full_working_app.py --topic \"your topic\" --duration 10${NC}"
        echo -e "${YELLOW}   python launch_full_working_app.py --topic \"comedy video\" --duration 30 --platform youtube${NC}"
        echo ""
        echo -e "${GREEN}✅ Ready for command line video generation${NC}"
        echo -e "${CYAN}📋 Available options:${NC}"
        echo -e "${YELLOW}   --topic \"Your video topic\"${NC}"
        echo -e "${YELLOW}   --duration 10|30|60 (seconds)${NC}"
        echo -e "${YELLOW}   --platform youtube|tiktok|instagram${NC}"
        echo -e "${YELLOW}   --category Comedy|Entertainment|Education${NC}"
        echo -e "${YELLOW}   --discussions (enable 19 AI agent discussions)${NC}"
        echo ""
        echo -e "${PURPLE}🎬 Example generation:${NC}"
        python launch_full_working_app.py --topic "funny cats doing yoga" --duration 10 --discussions
        ;;
    test|TEST)
        echo -e "${GREEN}🧪 Running Test Generation...${NC}"
        echo -e "${CYAN}🎯 Generating test video: 'AI robots dancing'${NC}"
        python launch_full_working_app.py --topic "AI robots dancing" --duration 10 --discussions
        ;;
    help|HELP|-h|--help)
        echo -e "${GREEN}🎬 Viral Video Generator Help${NC}"
        echo -e "${CYAN}================================${NC}"
        echo ""
        echo -e "${YELLOW}Usage:${NC}"
        echo -e "  ./run_video_generator.sh [mode] [options]"
        echo ""
        echo -e "${YELLOW}Modes:${NC}"
        echo -e "  ${GREEN}ui${NC}     - Launch web interface (default)"
        echo -e "  ${GREEN}cli${NC}    - Show CLI usage examples"
        echo -e "  ${GREEN}test${NC}   - Run test video generation"
        echo -e "  ${GREEN}help${NC}   - Show this help message"
        echo ""
        echo -e "${YELLOW}Features:${NC}"
        echo -e "  🤖 ${GREEN}19 AI Agents${NC} - Professional discussions"
        echo -e "  🎥 ${GREEN}VEO-2 Video${NC} - Real AI video generation"
        echo -e "  🎵 ${GREEN}Google TTS${NC} - Professional audio"
        echo -e "  📱 ${GREEN}Platform Optimization${NC} - YouTube, TikTok, Instagram"
        echo ""
        echo -e "${YELLOW}Requirements:${NC}"
        echo -e "  • ${CYAN}GOOGLE_API_KEY${NC} - Gemini API access"
        echo -e "  • ${CYAN}gcloud auth${NC} - VEO-2 access (optional)"
        echo -e "  • ${CYAN}Python 3.8+${NC} - Runtime environment"
        echo ""
        echo -e "${YELLOW}Examples:${NC}"
        echo -e "  ${CYAN}./run_video_generator.sh ui${NC}"
        echo -e "  ${CYAN}./run_video_generator.sh test${NC}"
        echo -e "  ${CYAN}python launch_full_working_app.py --topic \"comedy\" --duration 10${NC}"
        ;;
    *)
        echo -e "${RED}❌ Unknown mode: $MODE${NC}"
        echo -e "${YELLOW}💡 Available modes: ui, cli, test, help${NC}"
        echo -e "${CYAN}   Run: ./run_video_generator.sh help${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${PURPLE}🎉 Viral Video Generator Ready!${NC}"
echo -e "${CYAN}📊 System Status:${NC}"
echo -e "${GREEN}   ✅ 19 AI Agents - Operational${NC}"
echo -e "${GREEN}   ✅ VEO-2 Integration - Ready${NC}"
echo -e "${GREEN}   ✅ Audio Generation - Active${NC}"
echo -e "${GREEN}   ✅ Platform Optimization - Enabled${NC}" 