#!/bin/bash
# ViralAI Environment Setup Script v2.5.0-rc1
# Sets up complete development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ViralAI Environment Setup v2.5.0-rc1${NC}"
echo "============================================="

# Check Python version
echo -e "${BLUE}🐍 Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${GREEN}✅ Python version is compatible${NC}"
else
    echo -e "${RED}❌ Python 3.8+ required. Current: $python_version${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}⬆️  Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}📥 Installing dependencies...${NC}"
pip install -r requirements.txt

# Check for environment file
if [ ! -f "config.env" ]; then
    if [ -f "config.env.example" ]; then
        echo -e "${YELLOW}📋 Creating config.env from example...${NC}"
        cp config.env.example config.env
        echo -e "${YELLOW}⚠️  Please edit config.env with your API keys${NC}"
    else
        echo -e "${RED}❌ No config.env.example found${NC}"
    fi
else
    echo -e "${GREEN}✅ config.env already exists${NC}"
fi

# Check Google Cloud authentication
echo -e "${BLUE}🔐 Checking Google Cloud authentication...${NC}"
if command -v gcloud >/dev/null 2>&1; then
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Google Cloud authentication active${NC}"
    else
        echo -e "${YELLOW}⚠️  Run: gcloud auth login${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Google Cloud SDK not installed. Visit: https://cloud.google.com/sdk/docs/install${NC}"
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p outputs logs cache data/sessions
echo -e "${GREEN}✅ Directories created${NC}"

# Test basic imports
echo -e "${BLUE}🧪 Testing basic imports...${NC}"
python -c "
import sys
try:
    import moviepy
    import google.cloud
    import openai
    print('✅ All core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

echo -e "\n${GREEN}🎉 Environment setup complete!${NC}"
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Edit config.env with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Test with: python main.py --help"
echo "4. Run tests: ./scripts/run_tests.sh"