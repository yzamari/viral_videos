#!/bin/bash

# 🚀 AI Video Generator with Intelligent Agents - Quick Start
# Complete setup with voice selection, punctuation enhancement, and AI positioning

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║       🎬 AI Video Generator with Smart Agents            ║"
echo "║     Voice Selection • Punctuation • Style • Positioning   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Virtual Environment
echo -e "${BLUE}[1/6]${NC} Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
echo -e "${GREEN}✅ Virtual environment ready${NC}"

# Step 2: Dependencies
echo -e "${BLUE}[2/6]${NC} Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Configuration
echo -e "${BLUE}[3/6]${NC} Setting up configuration..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo -e "${YELLOW}⚠️  Please add your Google AI Studio API key to .env${NC}"
    echo "   GOOGLE_API_KEY=your_api_key_here"
    echo
    read -p "Press Enter after adding your API key..."
fi
echo -e "${GREEN}✅ Configuration ready${NC}"

# Step 4: Create outputs directory
echo -e "${BLUE}[4/6]${NC} Setting up output directories..."
mkdir -p outputs
mkdir -p logs
echo -e "${GREEN}✅ Directories created${NC}"

# Step 5: AI Agents Test
echo -e "${BLUE}[5/6]${NC} Testing AI agents integration..."
python3 -c "
try:
    from config.config import settings
    import google.generativeai as genai
    
    if not settings.google_api_key:
        print('❌ API key missing in .env file')
        exit(1)
    
    print('✅ API key configured')
    genai.configure(api_key=settings.google_api_key)
    print('✅ Google AI connection successful')
    
    # Test AI agents
    from src.agents.voice_director_agent import VoiceDirectorAgent
    from src.agents.visual_style_agent import VisualStyleAgent
    from src.agents.overlay_positioning_agent import OverlayPositioningAgent
    
    print('✅ VoiceDirectorAgent loaded')
    print('✅ VisualStyleAgent loaded')
    print('✅ OverlayPositioningAgent loaded')
    print('✅ All AI agents ready!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    exit(1)
"
echo -e "${GREEN}✅ AI agents test passed${NC}"

# Step 6: Ready to use
echo -e "${BLUE}[6/6]${NC} Setup complete!"
echo
echo -e "${GREEN}🎉 Ready to generate videos with intelligent AI agents!${NC}"
echo
echo -e "${BLUE}🤖 Available AI Agents:${NC}"
echo "  🎤 VoiceDirectorAgent - Smart voice selection (8 personalities)"
echo "  🎨 VisualStyleAgent - Dynamic style decisions (10+ styles)"
echo "  🎯 OverlayPositioningAgent - Smart subtitle positioning"
echo "  📝 EnhancedScriptProcessor - Punctuation & TTS optimization"
echo "  🌍 MultilingualTTS - 14+ language support"
echo
echo "Quick commands to try:"
echo
echo -e "${YELLOW}# Generate with AI voice selection${NC}"
echo "python3 main.py generate --mission 'convince people that quantum computing will revolutionize their daily lives' --duration 15 --platform tiktok"
echo
echo -e "${YELLOW}# Test AI agents specifically${NC}"
echo "python3 test_ai_agents_integration.py"
echo
echo -e "${YELLOW}# Test humorous TikTok missions${NC}"
echo "python3 test_simple_humorous_tiktok.py"
echo
echo -e "${YELLOW}# Launch modern UI${NC}"
echo "python3 modern_ui.py"
echo
echo -e "${BLUE}🎯 Features:${NC}"
echo "  ✅ Intelligent voice selection based on content analysis"
echo "  ✅ Perfect punctuation for natural speech"
echo "  ✅ Smart subtitle positioning (platform-optimized)"
echo "  ✅ Dynamic visual style selection"
echo "  ✅ Multi-language support with cultural adaptation"
echo "  ✅ Sentence protection (never cuts mid-sentence)"
echo
echo -e "${BLUE}📚 Documentation:${NC} README.md"
echo -e "${BLUE}🆘 Help:${NC} python3 main.py --help"
echo
echo -e "${GREEN}✨ Happy creating with intelligent AI agents! 🎬🤖${NC}" 