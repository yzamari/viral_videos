#!/bin/bash

# 🚀 Enhanced Viral Video Generator v2.0 - Launch Script
# Professional-grade viral video generation with 26+ AI agents

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Display header
clear
print_header "╔══════════════════════════════════════════════════════════════╗"
print_header "║          🎬 Enhanced Viral Video Generator v2.0              ║"
print_header "║       Professional AI-Powered Video Creation System          ║"
print_header "║                                                              ║"
print_header "║  🤖 26+ AI Agents with Senior Manager Supervision           ║"
print_header "║  🎬 VEO-2 Video Generation with Google Cloud TTS            ║"
print_header "║  📊 Real-time Monitoring and Analytics                      ║"
print_header "║  🎛️ Multiple Interfaces (CLI + Web UI)                      ║"
print_header "╚══════════════════════════════════════════════════════════════╝"
echo

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate
print_success "Virtual environment activated"

# Install/update dependencies
print_status "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_success "Dependencies installed"

# Check configuration
if [ ! -f "config.env" ]; then
    print_warning "Configuration file not found"
    if [ -f "config.env.example" ]; then
        print_status "Copying example configuration..."
        cp config.env.example config.env
        print_warning "Please edit config.env with your API keys before continuing"
        echo
        echo "Required configuration:"
        echo "  GOOGLE_API_KEY=your_google_ai_studio_key"
        echo
        read -p "Press Enter after configuring your API keys..."
    else
        print_error "No configuration template found"
        exit 1
    fi
fi

# Verify API key is configured
if ! grep -q "GOOGLE_API_KEY=.*[^[:space:]]" config.env; then
    print_error "GOOGLE_API_KEY not configured in config.env"
    print_status "Please add your Google AI Studio API key to config.env"
    exit 1
fi

print_success "Configuration verified"

# Function to show usage menu
show_menu() {
    echo
    print_header "🎯 Select an option:"
    echo "1) 🎬 Generate Video (Command Line)"
    echo "2) 🖥️  Launch Web Interface"
    echo "3) 📊 Show System Status"
    echo "4) 📁 View Recent Sessions"
    echo "5) 🧪 Run Quick Test"
    echo "6) 📚 Show Documentation"
    echo "7) 🚪 Exit"
    echo
}

# Function to generate video via CLI
generate_video_cli() {
    echo
    print_header "🎬 Video Generation Setup"
    
    # Get user input
    read -p "Enter video mission: " mission
if [ -z "$mission" ]; then
    mission="Create engaging content about AI capabilities"
    print_status "Using default mission: $mission"
fi
    
    read -p "Enter duration (5-60 seconds) [30]: " duration
    if [ -z "$duration" ]; then
        duration=30
    fi
    
    echo "Categories: Comedy, Educational, Entertainment, News, Tech"
    read -p "Enter category [Comedy]: " category
    if [ -z "$category" ]; then
        category="Comedy"
    fi
    
    echo "Platforms: youtube, tiktok, instagram, twitter"
    read -p "Enter platform [youtube]: " platform
    if [ -z "$platform" ]; then
        platform="youtube"
    fi
    
    echo "Discussion modes: light, standard, deep"
    read -p "Enter discussion mode [standard]: " discussions
    if [ -z "$discussions" ]; then
        discussions="standard"
    fi
    
    echo
    print_status "Starting video generation..."
    print_status "Mission: $mission"
    print_status "Duration: ${duration}s"
    print_status "Category: $category"
    print_status "Platform: $platform"
    print_status "Discussion Mode: $discussions"
    echo
    
    # Generate video
    python3 main.py generate \
        --mission "$mission" \
        --duration "$duration" \
        --category "$category" \
        --platform "$platform" \
        --discussions "$discussions"
    
    if [ $? -eq 0 ]; then
        print_success "Video generation completed!"
        print_status "Check the outputs/ directory for your video"
    else
        print_error "Video generation failed"
    fi
}

# Function to launch web interface
launch_web_ui() {
    echo
    print_status "Launching web interface..."
    print_status "The UI will be available at: http://localhost:7860"
    print_status "Press Ctrl+C to stop the web interface"
    echo
    
    # Check if port is available
    if lsof -Pi :7860 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 7860 is already in use"
        print_status "Trying alternative port 7861..."
        python3 simple_test_ui.py
    else
        python3 simple_test_ui.py
    fi
}

# Function to show system status
show_system_status() {
    echo
    print_header "📊 System Status"
    
    print_status "Python version: $(python3 --version)"
    print_status "Virtual environment: $(if [ -n "$VIRTUAL_ENV" ]; then echo "✅ Active"; else echo "❌ Not active"; fi)"
    
    # Check dependencies
    print_status "Checking dependencies..."
    python3 -c "
import sys
try:
    import gradio
    print('✅ Gradio:', gradio.__version__)
except ImportError:
    print('❌ Gradio: Not installed')

try:
    import google.generativeai
    print('✅ Google AI: Available')
except ImportError:
    print('❌ Google AI: Not installed')

try:
    from config.config import settings
    print('✅ Configuration: Loaded')
    if settings.google_api_key:
        print('✅ API Key: Configured')
    else:
        print('❌ API Key: Missing')
except Exception as e:
    print('❌ Configuration:', str(e))
"
    
    # Check output directory
    if [ -d "outputs" ]; then
        session_count=$(ls -1 outputs/session_* 2>/dev/null | wc -l)
        video_count=$(ls -1 outputs/final_video_*.mp4 2>/dev/null | wc -l)
        print_status "Output directory: ✅ Exists"
        print_status "Sessions created: $session_count"
        print_status "Videos generated: $video_count"
    else
        print_status "Output directory: ❌ Not found"
    fi
}

# Function to view recent sessions
view_recent_sessions() {
    echo
    print_header "📁 Recent Sessions"
    
    if [ -d "outputs" ]; then
        # List recent sessions
        sessions=$(ls -1t outputs/session_* 2>/dev/null | head -5)
        if [ -n "$sessions" ]; then
            print_status "Last 5 sessions:"
            echo
            for session in $sessions; do
                session_id=$(basename "$session")
                timestamp=$(echo "$session_id" | sed 's/session_//' | sed 's/_/ /')
                
                # Check for video file
                video_file=$(ls outputs/final_video_*.mp4 2>/dev/null | grep "${session_id#session_}" | head -1)
                if [ -n "$video_file" ]; then
                    size=$(ls -lh "$video_file" | awk '{print $5}')
                    echo "  📹 $session_id (${size})"
                else
                    echo "  📁 $session_id"
                fi
                
                # Check for discussions
                if [ -d "$session/agent_discussions" ]; then
                    discussion_count=$(ls -1 "$session/agent_discussions"/*.md 2>/dev/null | wc -l)
                    echo "     💬 $discussion_count discussions"
                fi
                echo
            done
        else
            print_status "No sessions found"
        fi
    else
        print_warning "No outputs directory found"
    fi
}

# Function to run quick test
run_quick_test() {
    echo
    print_header "🧪 Running Quick Test"
    print_status "Generating a 15-second test video..."
    
    python3 main.py generate \
        --mission "Quick AI test" \
        --duration 15 \
        --category Comedy \
        --discussions light
    
    if [ $? -eq 0 ]; then
        print_success "Quick test completed successfully!"
    else
        print_error "Quick test failed"
    fi
}

# Function to show documentation
show_documentation() {
    echo
    print_header "📚 Documentation"
    
    echo "Available documentation:"
    echo
    echo "📖 Main Documentation:"
    if [ -f "README.md" ]; then
        echo "  ✅ README.md - Main project documentation"
    fi
    if [ -f "RUNNING_INSTRUCTIONS.md" ]; then
        echo "  ✅ RUNNING_INSTRUCTIONS.md - Comprehensive usage guide"
    fi
    
    echo
    echo "📁 Detailed Guides:"
    if [ -f "docs/SYSTEM_ARCHITECTURE.md" ]; then
        echo "  ✅ docs/SYSTEM_ARCHITECTURE.md - Technical architecture"
    fi
    if [ -f "docs/WORKFLOW_GUIDE.md" ]; then
        echo "  ✅ docs/WORKFLOW_GUIDE.md - Complete command reference"
    fi
    if [ -f "docs/AI_AGENTS_COMPLETE_GUIDE.md" ]; then
        echo "  ✅ docs/AI_AGENTS_COMPLETE_GUIDE.md - AI agent system"
    fi
    if [ -f "docs/FEATURES_VERIFICATION.md" ]; then
        echo "  ✅ docs/FEATURES_VERIFICATION.md - Feature status"
    fi
    
    echo
    echo "🚀 Quick Commands:"
    echo "  python3 main.py --help                    # Show all options"
    echo "  python3 main.py generate --mission 'test'   # Generate video"
    echo "  python3 simple_test_ui.py                 # Launch web UI"
    echo
}

# Main menu loop
while true; do
    show_menu
    read -p "Choose option (1-7): " choice
    
    case $choice in
        1)
            generate_video_cli
            ;;
        2)
            launch_web_ui
            ;;
        3)
            show_system_status
            ;;
        4)
            view_recent_sessions
            ;;
        5)
            run_quick_test
            ;;
        6)
            show_documentation
            ;;
        7)
            echo
            print_success "Thank you for using Enhanced Viral Video Generator!"
            print_status "🎬 Create amazing viral content with 26+ AI agents! ✨"
            echo
            exit 0
            ;;
        *)
            print_error "Invalid option. Please choose 1-7."
            ;;
    esac
    
    echo
    read -p "Press Enter to continue..."
done 