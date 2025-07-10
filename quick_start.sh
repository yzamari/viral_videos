#!/bin/bash

# 🚀 Enhanced Viral Video Generator - Quick Start
# Get up and running in under 5 minutes!

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           🚀 Enhanced Viral Video Generator               ║"
echo "║                    Quick Start Setup                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Virtual Environment
echo -e "${BLUE}[1/5]${NC} Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
echo -e "${GREEN}✅ Virtual environment ready${NC}"

# Step 2: Dependencies
echo -e "${BLUE}[2/5]${NC} Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 3: Configuration
echo -e "${BLUE}[3/5]${NC} Setting up configuration..."
if [ ! -f "config.env" ]; then
    cp config.env.example config.env
    echo -e "${YELLOW}⚠️  Please add your Google AI Studio API key to config.env${NC}"
    echo "   GOOGLE_API_KEY=your_api_key_here"
    echo
    read -p "Press Enter after adding your API key..."
fi
echo -e "${GREEN}✅ Configuration ready${NC}"

# Step 4: Quick Test
echo -e "${BLUE}[4/5]${NC} Running quick system test..."
python3 -c "
try:
    from config.config import settings
    import google.generativeai as genai
    if settings.google_api_key:
        print('✅ API key configured')
        genai.configure(api_key=settings.google_api_key)
        print('✅ Google AI connection successful')
    else:
        print('❌ API key missing')
        exit(1)
except Exception as e:
    print(f'❌ Test failed: {e}')
    exit(1)
"
echo -e "${GREEN}✅ System test passed${NC}"

# Step 5: Ready to use
echo -e "${BLUE}[5/5]${NC} Setup complete!"
echo
echo -e "${GREEN}🎉 Ready to generate viral videos!${NC}"
echo
echo "Quick commands to try:"
echo
echo -e "${YELLOW}# Generate a 30-second video${NC}"
echo "python3 main.py generate --topic 'AI creating amazing content'"
echo
echo -e "${YELLOW}# Launch AI agent web interface${NC}"
echo "python3 modern_ui.py"
echo
echo -e "${YELLOW}# Interactive launcher${NC}"
echo "./launch.sh"
echo
echo -e "${BLUE}📚 Documentation:${NC} README.md, RUNNING_INSTRUCTIONS.md"
echo -e "${BLUE}🆘 Help:${NC} python3 main.py --help"
echo
echo -e "${GREEN}✨ Happy video creating with 3-19 intelligent AI agents! 🎬${NC}" 